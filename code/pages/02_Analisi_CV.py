import logging
import streamlit as st
import os
import re
import traceback
from utilities.LLMHelper import LLMHelper
from utilities.AzureFormRecognizerClient import AzureFormRecognizerClient
from collections import OrderedDict
import time
import json
import pandas as pd
import uuid
import re
from utilities.AzureBlobStorageClient import AzureBlobStorageClient
import io
from utilities.StreamlitHelper import StreamlitHelper
from utilities.AzureCosmosDBClient import AzureCosmosDBClient

logger = logging.getLogger(
    'azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)

def reset(profile, resume):

    client = AzureCosmosDBClient()
    logger.info("Reset analisi")
    logger.info("Cancellazione analisi id " +
                resume['id'] + " per il profilo "+profile)
    client.delete_analysis_by_candidate_id_and_profile(resume['id'], profile)
    logger.info("Analisi cancellata")
    st.success("Analisi cancellata con successo")


def valutazione(profile, resume):
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
            cv = client.download_blob_to_bytes(
                "resumes", resume['resume_id']+".pdf")
            prompts = list(cosmos_client.get_profile_by_id(profile))[
                0]['prompts']
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
                print(prompt['output'])
                score = re.findall(
                    r"Punteggio: (\d+)", prompt["output"])
                logger.info(score)
                try:
                    total_score = total_score + int(score[0])
                except:
                    logger.error("Errore nel calcolo del punteggio")
                progress = int(30 + 70 * (index + 1) / len(prompts))
                progress_bar.progress(progress, text=f"Analisi " +
                                      prompt["description"])

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

        # st.button(label="Reset Analisi Precedente",on_click=reset, args=(profile, resume,))

        for prompt in prompts:
            logger.info(prompt["description"])
            logger.info(prompt["output"])
            score = re.findall(r"Punteggio: (\d+)", prompt["output"])
            logger.info(score)
            if len(score) > 0:
                logger.info(f"Punteggio: {score[0]}")
                # score = ":green["+score[0]+"]"
                score = score[0]
            else:
                logger.info("Punteggio non trovato")
                # score = ":red[N/A]"
                score = "N/A"

            with st.expander(prompt["description"]+" "+score, expanded=False):
                st.markdown(prompt["output"])

    except Exception as e:
        error_string = traceback.format_exc()
        st.error(error_string)


try:
    st.set_page_config(layout="wide")
    StreamlitHelper.setup_session_state()
    StreamlitHelper.hide_footer()

    st.title("Analisi e Calcolo Punteggi per CV")
    st.markdown(
        "### In questa pagina è possibile caricare un CV e ottenere una valutazione del CV rispetto a profili diversi")
    st.markdown("#### Seleziona profilo")

    cosmos_client = AzureCosmosDBClient()
    # Get all profiles
    profiles = cosmos_client.get_profiles()
    profiles_description = [profile["profile_id"] for profile in profiles]
    profile = st.selectbox("Profilo:", profiles_description, key="profile")

    st.markdown("#### Seleziona candidato")

    resumes = cosmos_client.get_candidate_by_profile(profile)

    # resumes = [x['name'] for x in resumes]
    # resume = st.selectbox("Resumes", resumes)

    # # Show candidates table
    colms = st.columns((1, 1, 1, 1, 1, 1, 1, 1))
    fields = ['Nome',
              'Cognome',
              'Analisi Punteggio', '',
              'Valutazione Presente',
              'Anzianità Presente',
              'Analisi Effettuata',
              'Punteggio attuale']
    
    for col, field_name in zip(colms, fields):
        # header
        col.write(field_name)

    for resume in resumes:
        analyses = cosmos_client.get_analysis_by_candidate_id_and_profile(
            candidate_id=resume['id'], profile_id=profile)

        analyses = list(analyses)

        if len(analyses) == 1:
            analysis = analyses[0]
            resume['Analisi Punteggio'] = analysis['Score']
            resume['Analisi Effettuata'] = "Sì"
        else:
            resume['Analisi Punteggio'] = "N/A"
            resume['Analisi Effettuata'] = "No"

        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(
            (1, 1, 1, 1, 1, 1, 1, 1))
        col1.write(resume['Nome'])  # Nome
        col2.write(resume['Cognome'])  # Cognome
        button_phold = col3.empty()  # create a placeholder
        do_analysis = button_phold.button(
            "Recupera Analisi", key=resume['resume_id'])
        if do_analysis:
            output = valutazione(profile, resume)
        col4.empty()
        button_phold = col4.empty()
        do_reset = button_phold.button(
            "Reset Valutazione", key='reset'+resume['resume_id'], disabled=resume['Analisi Effettuata'] == "No")
        if do_reset:
            reset(profile, resume)
        # Valutazione Presente
        col5.write('Sì' if 'Valutazioni' in resume else 'No')
        # Anzianità Presente
        col6.write("Sì" if 'Storia Rapporto Lavorativo' in resume else "No")
        col7.write(resume['Analisi Effettuata'])
        col8.write(resume['Analisi Punteggio'])

except Exception as e:
    st.error(traceback.format_exc())
