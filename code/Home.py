from dotenv import load_dotenv
load_dotenv()

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
    st.session_state["temperature"] = st.slider("Temperature", 0.0, 1.0, 0.0)
    
except Exception:
    st.error(traceback.format_exc())
