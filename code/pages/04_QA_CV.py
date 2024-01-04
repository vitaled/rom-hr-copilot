import streamlit as st
from os import path
import traceback
import base64
from utilities.LLMHelper import LLMHelper
from utilities.AzureBlobStorageClient import AzureBlobStorageClient
from utilities.StreamlitHelper import StreamlitHelper
from utilities.AzureCosmosDBClient import AzureCosmosDBClient
import logging as logger

def ask_question():

    llm_helper = LLMHelper(temperature=0, max_tokens=1000)
    prompt_ask = st.session_state["prompt_ask"]
    cv_text = st.session_state["cv_text"]
    prompt_ask = f"Dato il seguente CV: {cv_text}\n Rispondi alla seguente domanda: {prompt_ask}"

    answer = llm_helper.get_qa_completion(prompt_ask)

    st.session_state["answer"] = answer 


def get_resume(resume):
    logger.info(f"Recupero CV {resume}")
    if resume:
        client = AzureBlobStorageClient()
        cv = client.download_blob_to_bytes("resumes", f"{resume}.pdf")

        base64_pdf = base64.b64encode(cv).decode('utf-8')
        st.session_state["resume_pdf"] = base64_pdf

        cosmos_client = AzureCosmosDBClient()
        resumes = list(cosmos_client.get_resume_by_id(resume))
        st.session_state["cv_text"] = resumes[0]["text"]

try:
    st.set_page_config(layout="wide")
    StreamlitHelper.setup_session_state()
    StreamlitHelper.hide_footer()
    st.title("Visualizza e Interrogazione CV")
    st.markdown("In questa pagina è possibile visionare i CV sia nella forma originale che nella forma testuale")

    st.title("Seleziona curriculum vitae")
    client = AzureBlobStorageClient()
    cosmos_client = AzureCosmosDBClient()

    logger.info("Recupero lista CV")
    candidates = cosmos_client.get_candidates()
    
    #filter out candidates where there is no resume_id
    candidates_list = [candidate for candidate in candidates if "resume_id" in candidate]
    resume_ids = [candidate['resume_id'] for candidate in candidates_list]
    logger.info(f"CV trovati: {len(resume_ids)}")
    logger.info(resume_ids)

    choices = {}
    
    for candidate in candidates_list:
        if "resume_id" in candidate:
            choices[candidate["resume_id"]] = candidate['Nome'] + " " + candidate['Cognome']

    logger.info(choices)
    resume_id = st.selectbox("Candidato", resume_ids,format_func=lambda x: choices[x], key="resume_id")
    
    
    st.button("Visualizza", key="view", on_click=get_resume, args=(resume_id,))

    tab_pdf, tab_text, tab_ask = st.tabs(["PDF", "TEXT", "ASK"])

    with tab_pdf:
        if st.session_state.get('resume_pdf') is not None:
            pdf_display = f'<embed src="data:application/pdf;base64,{st.session_state["resume_pdf"]}" width="100%" height="1000px" />'
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.warning("Nessun CV selezionato")

    with tab_text:
        if st.session_state.get('resume_pdf') is not None:
            text_display = st.session_state["cv_text"]
            st.markdown(text_display, unsafe_allow_html=True)
        else:
            st.warning("Nessun CV selezionato")
    
    with tab_ask:
        first_component = st.container()
        second_component = st.container()

        with first_component:
            if st.session_state.get("answer") is not None:
                st.write(st.session_state["answer"])
            else:
                st.write("No answer yet")
        with second_component:
            with st.form("form", clear_on_submit=False):
                text = st.text_area(
                    "",
                    placeholder="Enter your prompt here:",
                    height=100,
                    key="prompt_ask"
                )
                st.form_submit_button("Invia", on_click=ask_question)
except Exception as e:
    st.error(traceback.format_exc())
