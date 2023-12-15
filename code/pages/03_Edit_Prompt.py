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
from utilities.LLMHelper import LLMHelper
from utilities.AzureFormRecognizerClient import AzureFormRecognizerClient
from collections import OrderedDict 
import time
import json
import pandas as pd
import re
from utilities.AzureBlobStorageClient import AzureBlobStorageClient
from utilities.StreamlitHelper import StreamlitHelper

def read_file(file: str):
  with open(os.path.join('prompts', file),'r', encoding='utf-8') as file:
    return file.read()
  
def write_file(file: str, content: str):
  with open(os.path.join('prompts', file),'w', encoding='utf-8') as file:
    file.write(content)
    
def salvataggio():
    try:
      StreamlitHelper.hide_footer()
      write_file("estrazione_esperienza_jd.txt",             st.session_state["prompt_estrazione_esperienza_jd"])
      write_file("estrazione_esperienza_cv.txt",             st.session_state["prompt_estrazione_esperienza_cv"])
      write_file("estrazione_industry.txt",                  st.session_state["prompt_estrazione_industry"])
      write_file("estrazione_requisiti_attivita.txt",        st.session_state["prompt_estrazione_requisiti_attivita"])
      write_file("estrazione_requisiti_certificazione.txt",  st.session_state["prompt_estrazione_requisiti_certificazione"])
      write_file("estrazione_requisiti_lingua.txt",          st.session_state["prompt_estrazione_requisiti_lingua"])
      write_file("estrazione_requisiti_specialistica.txt",   st.session_state["prompt_estrazione_requisiti_specialistica"])
      write_file("estrazione_requisiti_titolo.txt",          st.session_state["prompt_estrazione_requisiti_titolo"])
      write_file("estrazione_requisiti_trasversale.txt",     st.session_state["prompt_estrazione_requisiti_trasversale"])
      write_file("match_competenza_attivita.txt",            st.session_state["prompt_match_competenza_attivita"])
      write_file("match_competenza_certificazione.txt",      st.session_state["prompt_match_competenza_certificazione"])
      write_file("match_competenza_lingua.txt",              st.session_state["prompt_match_competenza_lingua"])
      write_file("match_competenza_specialistica.txt",       st.session_state["prompt_match_competenza_specialistica"])
      write_file("match_competenza_titolo.txt",              st.session_state["prompt_match_competenza_titolo"])
      write_file("match_industry.txt",                       st.session_state["prompt_match_industry"])
      write_file("trasformazione_requisiti_json.txt",        st.session_state["prompt_trasformazione_requisiti_json"])
      
    except Exception as e:
        error_string = traceback.format_exc()
        st.error(error_string)
        print(error_string)

try:
    StreamlitHelper.setup_session_state()
    st.set_page_config(layout="wide")
    profile = st.selectbox("Profilo:", ("Profilo n.1", "Profilo n.2", "Profilo n.3"),key="profile")
    
    st.title("Edit Prompt")
    
    if profile == "Profilo n.1":
          prompts = [
                {
                    "description": "Paragrafo 1: Area di Provenienza",
                    "text": "Paragrafo-1.txt"
                },
                {
                    "description": "Paragrafo 2: Titolo di Studio",
                    "text": "Paragrafo-2.txt"
                },
                {
                    "description": "Paragrafo 3.1: Competenze Professionali (1/2)",
                    "text": "Paragrafo-3.1.txt"
                },
                {
                    "description": "Paragrafo 3.2: Competenze Professionali (2/2)",
                    "text": "Paragrafo-3.2.txt"
                }
            ]
          
          for prompt in prompts:
            prompt_text = read_file(os.path.join('profilo01', prompt["text"]))
            st.session_state[prompt['description']] = st.text_area(label=prompt['description'],     value=prompt_text, height=300)
   
    elif profile == "Profilo n.2":
          st.error("Profilo non ancora implementato")
    elif profile == "Profilo n.3":
        st.error("Profilo non ancora implementato")   
    else:
        st.error("Profilo non riconosciuto")

    st.button(label="Salvataggio Prompt",disabled=True, on_click=salvataggio)
    
except Exception as e:
    st.error(traceback.format_exc())