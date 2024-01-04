# Prompt Livello OK
# Prompt Anni esperienza richiesti da JD OK
# Prompt Industry OK
# Prompt Skill OK
# Prompt Lingua OK (split lingua)
# Prompt Certificazioni OK

import logging as logger
import streamlit as st
import os
import traceback
from utilities.StreamlitHelper import StreamlitHelper
from utilities.AzureCosmosDBClient import AzureCosmosDBClient

def read_file(file: str):
  with open(os.path.join('prompts', file),'r', encoding='utf-8') as file:
    return file.read()
  
def write_file(file: str, content: str):
  with open(os.path.join('prompts', file),'w', encoding='utf-8') as file:
    file.write(content)
    
def salvataggio():
      
    try:
      logger.info("Salvataggio profilo")
      cosmos_client = AzureCosmosDBClient()
      profile = st.session_state['current_profile']
      for index, prompt in enumerate(profile['prompts']):
            profile['prompts'][index]['text']= st.session_state[prompt['description']]
      logger.info(profile)
      cosmos_client.update_profile(profile)
      st.success("Salvataggio Completato")
    except Exception as e:
        error_string = traceback.format_exc()
        st.error(error_string)
        logger.error(error_string)

try:
    st.set_page_config(layout="wide")
    StreamlitHelper.setup_session_state()
    StreamlitHelper.hide_footer()

    cosmos_client = AzureCosmosDBClient()

    profiles = cosmos_client.get_profiles()
    profiles_description = [profile["profile_id"] for profile in profiles]
    profile = st.selectbox("Profilo:", profiles_description,key="profile")

    st.title("Modifica Prompts")
    profile = list(cosmos_client.get_profile_by_id(profile))[0]
    st.session_state["current_profile"] = profile
    for prompt in profile['prompts']:
        tab_text, tab_markdown = st.tabs(["Testo Prompt", "Preview Markdown"])
        with tab_text:
           st.session_state[prompt['description']] = st.text_area(label=prompt['description'],value=prompt['text'], height=300)
        with tab_markdown:
           st.markdown(st.session_state[prompt['description']])
            
        #st.session_state[prompt['description']] = st.text_area(label=prompt['description'],value=prompt['text'], height=300)

    st.button(label="Salvataggio Prompt",disabled=False, on_click=salvataggio)
    
except Exception as e:
    st.error(traceback.format_exc())