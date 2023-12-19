from dotenv import load_dotenv
load_dotenv()
from st_pages import Page, show_pages, add_page_title
import streamlit as st
import os
import traceback
from utilities.LLMHelper import LLMHelper
import logging
from utilities.StreamlitHelper import StreamlitHelper

logger = logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)

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

try:
   # Optional -- adds the title and icon to the current page
    #add_page_title()

    # Specify what pages should be shown in the sidebar, and what their titles and icons
    # should be
    show_pages(
        [
            Page("Home.py", "Home"),
            Page("pages/01_Aggiunta_CV.py", "Aggiungi CV"),
            Page("pages/02_Analisi_CV.py", "Analisi CV",),
            Page("pages/03_Prompt.py", "Prompts"),    
            Page("pages/04_QA_CV.py", "QA CV", )
        ]
    )

    st.set_page_config(layout="wide")
    StreamlitHelper.hide_footer()

    st.title("HR Assistant Open AI")
    
    llm_helper = LLMHelper()

    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        st.write("")
        st.image(os.path.join('images','citta-metropolitana-roma-capitale-logo.png'))
    with col3:
        st.button("Controllo Deployment", on_click=check_deployment)
 
    st.session_state["token_response"] = st.slider("Tokens response length", 100, 1500, 1000)
    st.session_state["temperature"] = st.slider("Temperature", 0.0, 1.0, 0.7)
    
except Exception:
    st.error(traceback.format_exc())
