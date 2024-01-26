from utilities.User import User
from streamlit.web.server.websocket_headers import _get_websocket_headers
from streamlit.web.server.server import Server
from utilities.StreamlitHelper import StreamlitHelper
# from utilities.SessionHelper import SessionHelper

from utilities.LLMHelper import LLMHelper
import traceback
import os
import streamlit as st
from st_pages import Page, show_pages, add_page_title
from dotenv import load_dotenv
load_dotenv()
from st_pages import Page, show_pages, add_page_title
import streamlit as st
import os
import traceback
import logging
from utilities.StreamlitHelper import StreamlitHelper
from utilities.SessionHelper import SessionHelper

logger = logging.getLogger("CMRCVLog")#'azure.core.pipeline.policies.http_logging_policy')
logger.setLevel(logging.INFO)
try:
    st.set_page_config(layout="wide")
    StreamlitHelper.hide_footer()
    st.title("HR Assistant Open AI")
    st.image(os.path.join('images','citta-metropolitana-roma-capitale-logo.png'))   
    logger.info('Connecting to Home Page')
    user = SessionHelper.get_current_user()
    logger.info('Connected User: ' + user.get_name())
    st.title('Benvenuto: ' + user.get_name())
except Exception:
    st.error(traceback.format_exc())
