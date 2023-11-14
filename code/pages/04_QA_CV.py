import streamlit as st
from os import path
import mimetypes
import traceback
import base64
from utilities.LLMHelper import LLMHelper
from utilities.AzureBlobStorageClient import AzureBlobStorageClient


def ask_question():

    llm_helper = LLMHelper(temperature=0, max_tokens=1000)
    prompt_ask = st.session_state["prompt_ask"]
    cv_text = st.session_state["cv_text"].decode('utf-8')
    prompt_ask = f"Dato il seguente CV: {cv_text}\n Rispondi alla seguente domanda: {prompt_ask}"

    answer = llm_helper.get_qa_completion(prompt_ask)

    st.session_state["answer"] = answer


def get_resume(resume):
    if resume:
        client = AzureBlobStorageClient()
        cv = client.download_blob_to_bytes("resumes", resume)

        base64_pdf = base64.b64encode(cv).decode('utf-8')
        st.session_state["resume_pdf"] = base64_pdf

        cv_text = client.download_blob_to_bytes("processed", resume+".txt")
        st.session_state["cv_text"] = cv_text


try:
    st.set_page_config(layout="wide")
    st.title("Visualizza e Interrogazione CV")
    st.markdown(
        "In questa pagina è possibile visionare i CV sia nella forma originale che nella forma testuale")

    st.title("Seleziona curriculum vitae")
    client = AzureBlobStorageClient()
    resumes = client.get_all_urls("resumes")
    resumes = [x['file'] for x in resumes]
    resume = st.selectbox("Resume", resumes)
    st.button("Visualizza", key="view", on_click=get_resume(resume))

    tab_pdf, tab_text, tab_ask = st.tabs(["PDF", "TEXT", "ASK"])

    with tab_pdf:
        if st.session_state.get('resume_pdf') is not None:
            pdf_display = f'<embed src="data:application/pdf;base64,{st.session_state["resume_pdf"]}" width="100%" height="1000px" />'
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.warning("Nessun CV selezionato")

    with tab_text:
        if st.session_state.get('resume_pdf') is not None:
            text_display = st.session_state["cv_text"].decode('utf-8')
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
