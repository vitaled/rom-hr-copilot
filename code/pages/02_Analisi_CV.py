import logging
from subprocess import PIPE, STDOUT
import streamlit as st
import re
import sys
import traceback
from utilities.LLMHelper import LLMHelper
from utilities.AzureFormRecognizerClient import AzureFormRecognizerClient
import json
import pandas as pd
import uuid
import re
from utilities.AzureBlobStorageClient import AzureBlobStorageClient
from utilities.StreamlitHelper import StreamlitHelper
from utilities.AzureCosmosDBClient import AzureCosmosDBClient
from utilities.SessionHelper import SessionHelper
from time import sleep
logger = logging.getLogger()#'azure.core.pipeline.policies.http_logging_policy')
logger.setLevel(logging.WARNING)


def batch_analysis(profile):
    arg_ids = ",".join(
        resume_id for resume_id in st.session_state['selected_resumes'])
    arg_temperature = st.session_state["temperature"]
    arg_max_tokens = st.session_state["token_response"]
    arg_profile = profile
    
    import subprocess
    command_line = [
        f"python",
        './scripts/batchCVAnalyses.py',
        '--temperature', str(arg_temperature),
        '--max-tokens', str(arg_max_tokens),
        '--profile', arg_profile,
        '--ids', arg_ids
    ]
    p = subprocess.Popen(command_line,stdout=PIPE,stderr=STDOUT,shell=True)
    sleep(1)
    st.toast("Processo di analisi CV iniziato")

def add_to_selection(resume_id):
    if 'selected_resumes' not in st.session_state:
        st.session_state['selected_resumes'] = []

    if st.session_state['selected_'+resume_id]:
        st.session_state['selected_resumes'].append(resume_id)
    else:
        st.session_state['selected_resumes'].remove(resume_id)


def reset(profile, resume):
    client = AzureCosmosDBClient()
    logger.info("Cancellazione analisi id " +
                resume['id'] + " per il profilo "+profile)
    st.session_state['analysis_'+resume['resume_id']] = None
    logger.info("Rimozione analisi dallo stato")
    client.delete_analysis_by_candidate_id_and_profile(resume['id'], profile)
    logger.info("Analisi cancellata dal database")
    st.toast("Analisi cancellata")
    st.rerun()


def print_analysis(analysis):
    text = ""
    for prompt in analysis:
        score = re.findall(r"Punteggio: (\d+)", prompt["output"])
        if len(score) > 0:
            logger.info(f"Punteggio: {score[0]}")
            score = score[0]
        else:
            logger.info("Punteggio non trovato")
            score = "N/A"

        with st.expander(prompt["description"]+" "+score, expanded=False):
            st.markdown(prompt["output"])
        text = text + prompt["description"] + \
            " "+score+"\n"+prompt["output"]+"\n\n"
    st.download_button("Scarica analisi", text, "analysis.txt", "txt")


def get_analysis(profile, resume):
    cosmos_client = AzureCosmosDBClient()
    analysis = None
    logger.info("Cercando analisi già eseguita per il candidato " +
                resume['id']+" e il profilo "+profile)
    analyses_query = cosmos_client.get_analysis_by_candidate_id_and_profile(
        candidate_id=resume['id'],
        profile_id=profile
    )
    logger.info(analyses_query)
    analyses = list(analyses_query)

    if len(analyses) == 1:
        logger.info("CV già analizzato")
        analysis = analyses[0]
        prompts = json.loads(analysis["Analysis"])
        return prompts
    else:
        return None


def analyze(profile, resume):
    try:
        cosmos_client = AzureCosmosDBClient()
        client = AzureBlobStorageClient()

        progress_bar = st.progress(0, text="Inizio Analisi")

        analysis = None
        logger.info("Cercando analisi già eseguita per il candidato " +
                    resume['id']+" e il profilo "+profile)
        analyses_query = cosmos_client.get_analysis_by_candidate_id_and_profile(
            candidate_id=resume['id'], profile_id=profile)
        logger.info(analyses_query)
        analyses = list(analyses_query)
        cv_text = None

        if len(analyses) == 1:
            logger.info("CV già analizzato")
            analysis = analyses[0]
            progress_bar.progress(90, text="Recupero Analisi Candidato")
            prompts = json.loads(analysis["Analysis"])
        else:
            total_score = 0
            logger.info("CV non ancora analizzato")
            progress_bar.progress(10, text="Recupero CV")
            cv = client.download_blob_to_bytes("resumes", resume['resume_id']+".pdf")
            prompts = list(cosmos_client.get_profile_by_id(profile))[0]['prompts']
            progress_bar.progress(20, text="Recupero Estrazione Testo")
            cv_text = list(cosmos_client.get_resume_by_id(
                resume['resume_id']))[0]['text']

            llm_helper = LLMHelper(
                temperature=st.session_state["temperature"], max_tokens=st.session_state["token_response"])

            progress_bar.progress(30, text="Impostazione analisi prompts")
            for index, prompt in enumerate(prompts):
                prompt_text = prompt["text"]
                prompt_text = prompt_text.replace('{cv}', cv_text)

                history_table = resume['Storia Rapporto Lavorativo']

                history_table = pd.DataFrame(history_table)
                history_table = history_table.to_markdown()
                prompt_text = prompt_text.replace(
                    '{storia_professionale}', history_table)
                evaluation_table = resume['Valutazioni']
                evaluation_table = pd.DataFrame(evaluation_table, index=[0])

                # Reset the index
                evaluation_table = evaluation_table.reset_index()
                # Use melt to pivot the DataFrame
                evaluation_table = evaluation_table.melt(
                    id_vars='index', var_name='Periodo', value_name='Valutazione')
                # Drop the 'index' column as it's not needed
                evaluation_table = evaluation_table.drop(columns='index')

                evaluation_table = evaluation_table.to_markdown()

                prompt_text = prompt_text.replace(
                    '{risultati_valutazioni}', evaluation_table)

                access_title = resume["Dichiaro di essere in possesso del titolo di studio richiesto per l’ammissione alla selezione:"]
                prompt_text = prompt_text.replace(
                    '{titolo_accesso}', access_title)

                access_title_info = resume["Indicare l'Istituto che lo ha rilasciato, la votazione riportata e la data di conseguimento"]
                prompt_text = prompt_text.replace(
                    '{dettagli_titolo_accesso}', access_title_info)

                other_titles = resume["Dichiaro di possedere titoli di studio ulteriori rispetto a quelli previsti per l’accesso all’Area di Funzionario/Elevata Qualificazione:"]
                prompt_text = prompt_text.replace(
                    '{altri_titoli}', other_titles)

                other_title_info = resume["Indicare l'Istituto che lo ha rilasciato, la votazione riportata e la data di conseguimento.1"]
                prompt_text = prompt_text.replace(
                    '{dettagli_altri_titoli}', other_title_info)

                prompt['output'] = llm_helper.get_hr_completion(prompt_text)
                score = re.findall(r"Punteggio: (\d+)", prompt["output"])

                try:
                    total_score = total_score + int(score[0])
                except:
                    logger.error("Errore nel calcolo del punteggio")
                progress = int(30 + 70 * (index + 1) / len(prompts))
                progress_bar.progress(
                    progress, text=f"Analisi " + prompt["description"])

            analysis = {
                "id": str(uuid.uuid4()),
                "AnalysisId": str(uuid.uuid4()),
                "CandidateId": resume['id'],
                "ProfileId": profile,
                "Analysis": json.dumps(prompts),
                "Text": cv_text,
                "Score": total_score
            }
            cosmos_client.put_analysis(analysis)
        progress_bar.progress(100, text="Analisi completata")
        progress_bar.empty()
        st.session_state['analysis_'+resume['resume_id']] = prompts
    except Exception as e:
        error_string = traceback.format_exc()
        st.error(error_string)


try:
    st.set_page_config(layout="wide")
    StreamlitHelper.setup_session_state()
    StreamlitHelper.hide_footer()
    user = SessionHelper.get_current_user()
    available_profiles = user.get_profiles()

    st.title("Analisi e Calcolo Punteggi per CV")
    st.markdown(
        "### In questa pagina è possibile caricare un CV e ottenere una valutazione del CV rispetto a profili diversi")
    st.markdown("#### Seleziona profilo")

    cosmos_client = AzureCosmosDBClient()
    # Get all profiles
    profiles = cosmos_client.get_profiles()
    profiles_description = [profile["profile_id"]
                            for profile in profiles if profile["profile_id"] in available_profiles]
    profile = st.selectbox("Profilo:", profiles_description, key="profile")

    st.markdown("#### Seleziona candidato")
    resumes = cosmos_client.get_candidate_by_profile(profile)

    # # Show candidates table
    colms = st.columns((1, 1, 1, 1, 1, 1, 1, 1, 2))
    fields = ['Seleziona',
              'Nome',
              'Cognome',
              'Valutazione Presente',
              'Anzianità Presente',
              'Analisi Effettuata',
              'Punteggio attuale',
              '',
              '']

    for col, field_name in zip(colms, fields):
        # header
        col.write(field_name)

    resumes_with_id = [resume for resume in resumes if 'resume_id' in resume]
    for resume in resumes_with_id:

        analyses = cosmos_client.get_analysis_by_candidate_id_and_profile(
            candidate_id=resume['id'], profile_id=profile)

        analyses = list(analyses)
        if len(analyses) == 1:
            logger.info("CV"+resume['id']+" già analizzato")
            analysis = analyses[0]
            resume['Analisi Punteggio'] = analysis['Score']
            resume['Analisi Effettuata'] = "Sì"
        else:
            logger.info("CV"+resume['id']+" non ancora analizzato")
            resume['Analisi Punteggio'] = "N/A"
            resume['Analisi Effettuata'] = "No"

        col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns(
            (1, 1, 1, 1, 1, 1, 1, 1, 2,))

        col1.checkbox("", key='selected_'+resume['resume_id'],
                      on_change=add_to_selection, args=(resume['resume_id'],))
        col2.write(resume['Nome'])  # Nome
        col3.write(resume['Cognome'])  # Cognome
        # Valutazione Presente
        col4.write('Sì' if 'Valutazioni' in resume else 'No')
        # Anzianità Presente
        col5.write("Sì" if 'Storia Rapporto Lavorativo' in resume else "No")

        exists_analysis = col6.empty()

        exists_analysis.write(resume['Analisi Effettuata'])
        st.session_state['exists_analysis_' +
                         resume['resume_id']] = exists_analysis

        score_phold = col7.empty()
        score_phold.write(resume['Analisi Punteggio'])

        # Analysis button
        button_phold = col8.empty()  # create a placeholder

        col8.button(
            "analizza",
            disabled=False, on_click=analyze, args=(profile, resume), key="analisys_"+resume['resume_id'])

        if 'analysis_'+resume['resume_id'] in st.session_state and st.session_state['analysis_'+resume['resume_id']] is not None:
            print_analysis(st.session_state['analysis_'+resume['resume_id']])

        # Reset button
        button_phold = col9.empty()
        do_reset = button_phold.button(
            "reset analisi",
            disabled=resume['Analisi Effettuata'] == "No",
            key="reset_"+resume['resume_id']
        )
        if do_reset:
            reset(profile, resume)
    st.button(label="Analizza selezionati",
              disabled=False if 'selected_resumes' in st.session_state and len(st.session_state['selected_resumes']) > 0 else True, on_click=batch_analysis, args=(profile,))
except Exception as e:
    st.error(traceback.format_exc())
