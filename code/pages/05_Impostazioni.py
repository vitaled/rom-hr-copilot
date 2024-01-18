from utilities.AzureCosmosDBClient import AzureCosmosDBClient
from utilities.StreamlitHelper import StreamlitHelper
import logging
from utilities.LLMHelper import LLMHelper
import traceback
import os
import streamlit as st
from st_pages import Page, show_pages, add_page_title
from dotenv import load_dotenv
import pandas as pd
import io
from utilities.AzureCosmosDBClient import AzureCosmosDBClient
import uuid
from utilities.SessionHelper import SessionHelper
load_dotenv()
logger = logging.getLogger('azure.core.pipeline.policies.http_logging_policy')
logger.setLevel(logging.WARNING)


def upload_candidates_data(uploaded_data):
    client = AzureCosmosDBClient()
    # create a dataframe from the uploaded file
    file = io.StringIO(uploaded_data.getvalue().decode("utf-8"))
    df = pd.read_csv(file, sep=";")
    df.fillna("", inplace=True)
    df.columns = [x.replace('&#039;', '\'') for x in df.columns]
    inserted_candidate = 0
    missing_candidate = 0
    ambigous_candidates = 0
    for row in df.iterrows():
        candidate = {}
        cf = row[1]['Codice Fiscale'].upper()
        candidates = list(client.get_candidate_by_cf(cf))

        if len(candidates) == 1:
            # Create a ner candidate
            candidate = candidates[0]
            for col in df.columns:
                candidate[col] = row[1][col]

            client.put_candidate(candidate)
            inserted_candidate += 1
        elif len(candidates) == 0:
            missing_candidate += 1
        else:
            st.error(f"Errore: più candidati trovati con codice fiscale {cf}")
            ambigous_candidates += 1

    st.success(f"Caricati {inserted_candidate} nuovi candidati. {missing_candidate} candidati non presenti nel database. {ambigous_candidates} candidati con codice fiscale ambiguo.")


def upload_evalations_data(uploaded_data):
    logging.info("Caricamento dati valutazioni")
    cosmos_client = AzureCosmosDBClient()
    file = io.BytesIO(uploaded_data.getvalue())
    df = pd.read_excel(file)
    df.fillna("", inplace=True)
    for row in df.iterrows():
        cf = row[1]['CodiceFiscale'].upper()
        candidates = list(cosmos_client.get_candidate_by_cf(cf))
        if candidates != []:
            candidate = candidates[0]
            candidate["Matricola"] = row[1]['Matricola']
            candidate["Valutazioni"] = {
                'III2020':  row[1]['III2020'],
                'IV2020': row[1]['IV2020'],
                'I2021': row[1]['I2021'],
                'II2021': row[1]['II2021'],
                'I2022': row[1]['I2022'],
                'II2022': row[1]['II2022'],
                'I2023': row[1]['I2023']
            }
            cosmos_client.put_candidate(candidate)


def upload_seniority_data(uploaded_data):
    logging.info("Caricamento dati anzianità")
    client = AzureCosmosDBClient()
    file = io.BytesIO(uploaded_data.getvalue())
    df = pd.read_excel(file)
    df.fillna("", inplace=True)
    candidate = {}
    print(df)
    for row in df.iterrows():
        if row[1]['Storico cod livello'] == 'LIVELLO ATTUALE':
            if candidate != {}:
                client.put_candidate(candidate)
            candidate = {}
            cf = row[1]['CodiceFiscale'].upper()
            # candidate["id"] = str(uuid.uuid4())
            candidate["id"] = cf
            candidate['CodiceFiscale'] = cf
            candidate['Matricola'] = row[1]['Matricola']
            candidate['Cognome'] = row[1]['Cognome']
            candidate['Nome'] = row[1]['Nome']
            candidate['Cod Reparto'] = row[1]['Cod Reparto']
            candidate['Reparto'] = row[1]['Reparto']
            candidate['Ex Cfl + varie'] = row[1]['Ex Cfl + varie']
            candidate['Posizione Giuridica attuale'] = row[1]['Posizione Giuridica attuale']
            candidate['Qualifica'] = row[1]['Qualifica']
            candidate['NConcorso'] = row[1]['NConcorso']
            candidate['Data assunzione'] = row[1]['Data assunzione'].strftime('%Y-%m-%d')
            candidate['Cod Livello attuale'] = row[1]['Cod Livello attuale']
            candidate['Storia Rapporto Lavorativo'] = []
        else:
            candidate['Storia Rapporto Lavorativo'].append({
                'Inizio rapp. lavorativo': row[1]['Inizio rapp. lavorativo'].strftime('%Y-%m-%d'),
                'Fine rapporto lavorativo': row[1]['Fine rapporto lavorativo'].strftime('%Y-%m-%d'),
                'Inizio inquadramento livello': row[1]['Inizio inquadramento livello'].strftime('%Y-%m-%d'),
                'Fine inquadramento livello': row[1]['Fine inquadramento livello'].strftime('%Y-%m-%d'),
                'Descrizione livello': row[1]['Descrizione livello']
            })


def check_deployment():
    try:
        llm_helper = LLMHelper()
        llm_helper.get_hr_completion("Generate a joke!")
        st.success("LLM is working!")

    except Exception as e:
        st.error(f"""LLM is not working.
            Please check you have a deployment name {llm_helper.deployment_name} in your Azure OpenAI resource {llm_helper.api_base}.    
            Then restart your application.
            """)
        st.error(traceback.format_exc())


def on_setting_change():
    st.session_state['settings_changed'] = True


def save_users():

    try:
        if st.session_state['settings_changed'] is False:
            st.error("Nessuna modifica da salvare")
        else:
            cosmos_client = AzureCosmosDBClient()
            users = cosmos_client.get_users()
            for user in users:
                user["role"] = "Admin" if st.session_state[user.get(
                    "id")+"_role"] else "User"
                user["profiles"] = st.session_state[user.get(
                    "id") + "_profiles"]
                cosmos_client.put_user(
                    user['id'], user['name'], user['role'], user['profiles'])
            st.session_state['settings_changed'] = False
            st.success("Salvataggio Completato")
    except Exception as e:
        error_string = traceback.format_exc()
        st.error(error_string)
        logger.error(error_string)


try:
    if "settings_changed" not in st.session_state:
        st.session_state["settings_changed"] = False
    cosmos_client = AzureCosmosDBClient()
    st.set_page_config(layout="wide")
    StreamlitHelper.hide_footer()

    st.title("Impostazioni HR Assistant Open AI")
    with st.expander("Impostazioni LLM", expanded=False):
        llm_helper = LLMHelper()
        st.session_state["token_response"] = st.slider(
            "Tokens response length", 500, 1500, 1000)
        st.session_state["temperature"] = st.slider(
            "Temperature", 0.0, 1.0, 0.7)
        st.button("Controllo Deployment", on_click=check_deployment)
    with st.expander("Dati Supporto", expanded=False):
        st.markdown("### Dati Caricati")
        employees_count = cosmos_client.get_candidates_with_candidacy_count()
        employees_with_history_count = cosmos_client.get_candidates_with_history_count()
        employees_with_evaluation_count = cosmos_client.get_candidates_with_evaluation_count()

        st.markdown(
            f"Impiegati con candidature attive: `{employees_count}`")
        st.markdown(
            f"Impiegati con storico caricato: `{employees_with_history_count}`")
        st.markdown(
            f"Impiegati con valutazione caricata: `{employees_with_evaluation_count}`")

        st.markdown("### Caricamento nuovi dati")
        st.markdown("""
                    - I dati devono essere caricati in formato testo, con un record per riga. 
                    - I campi devono essere separati da tabulazione. 
                    - I dati per i candidati vengono uniti sulla base del codice fiscale.
                    """)
        candidates_upload = st.file_uploader(
            "Caricamento dati candidati", type=None, accept_multiple_files=False)
        if candidates_upload is not None:
            if st.button("Carica Dati candidati"):
                try:
                    upload_candidates_data(candidates_upload)
                    st.success("Caricamento completato")
                except Exception as e:
                    st.error(traceback.format_exc())

        seniority_upload = st.file_uploader(
            "Caricamento dati anzianità", type=None, accept_multiple_files=False)
        if seniority_upload is not None:
            if st.button("Carica Dati Anzianità"):
                try:
                    upload_seniority_data(seniority_upload)
                    st.success("Caricamento completato")
                except Exception as e:
                    st.error(traceback.format_exc())

        evaluation_upload = st.file_uploader(
            "Caricamento dati valutazioni", type=None, accept_multiple_files=False)
        if evaluation_upload is not None:
            if st.button("Carica Dati Valutazioni"):
                try:
                    upload_evalations_data(evaluation_upload)
                    st.success("Caricamento completato")
                except Exception as e:
                    st.error(traceback.format_exc())
    
except:
    st.error(traceback.format_exc())
