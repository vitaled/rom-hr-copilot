from utilities.User import User
from streamlit.web.server.websocket_headers import _get_websocket_headers
from streamlit.web.server.server import Server
from utilities.StreamlitHelper import StreamlitHelper
# from utilities.SessionHelper import SessionHelper
import logging
from utilities.LLMHelper import LLMHelper
import traceback
import os
import streamlit as st
from st_pages import Page, show_pages, add_page_title
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(
    'azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)

try:
   # Optional -- adds the title and icon to the current page
    # add_page_title()

    # Specify what pages should be shown in the sidebar, and what their titles and icons
    # should be
    # show_pages(
    #     [
    #         Page("Home.py", "Home"),
    #         Page("pages/01_Aggiunta_CV.py", "Aggiungi CV Candidato"),
    #         Page("pages/02_Analisi_CV.py", "Analisi Candidato",),
    #         Page("pages/03_Prompt.py", "Gestione Profili"),
    #         Page("pages/04_QA_CV.py", "Q/A Candidato", ),
    #         Page("pages/05_Admin.py", "Impostazioni")
    #     ]
    # )

    st.set_page_config(layout="wide")
    StreamlitHelper.hide_footer()
    
    # headers = _get_websocket_headers()
    # # st.session_state['principal_name'] = headers.get('x-ms-client-principal-name',"dvitale@microsoft.com")
    # # st.session_state['principal_id'] = headers.get('x-ms-client-principal-id','cff054a1-bb8a-4e05-9218-9f3846d14ad8')

    # user = SessionHelper.get_current_user()

    st.title("Benvenuto nella pagina di HR Assistant Open AI")
    st.image(os.path.join('images', 'citta-metropolitana-roma-capitale-logo.png'))
    #st.markdown("Sei collegato come **" + user.get_name() + "** con ruolo "+ user.get_role() + ".")
except Exception:
    st.error(traceback.format_exc())
