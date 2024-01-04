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

try:
   # Optional -- adds the title and icon to the current page
    #add_page_title()

    # Specify what pages should be shown in the sidebar, and what their titles and icons
    # should be
    show_pages(
        [
            Page("Home.py", "Home"),
            Page("pages/01_Aggiunta_CV.py", "Aggiungi Candidato"),
            Page("pages/02_Analisi_CV.py", "Analisi Candidato",),
            Page("pages/03_Prompt.py", "Gestione Profili"),    
            Page("pages/04_QA_CV.py", "Q/A Candidato", ),
            Page("pages/05_Admin.py", "Impostazioni")
        ]
    )

    st.set_page_config(layout="wide")
    StreamlitHelper.hide_footer()

    st.title("HR Assistant Open AI")
    
    llm_helper = LLMHelper()
    st.image(os.path.join('images','citta-metropolitana-roma-capitale-logo.png'))
    
except Exception:
    st.error(traceback.format_exc())
