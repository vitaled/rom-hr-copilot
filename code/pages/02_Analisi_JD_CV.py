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
import io


def valutazione(profile,resume):
    try:
      logger.info(profile)
      client = AzureBlobStorageClient()
      my_bar = st.progress(0, text="Inizio Analisi")

      my_bar.progress(10, text="Recupero CV")
      cv = client.download_blob_to_bytes("resumes",resume)

      my_bar.progress(20, text="Estrazione Testo")
      form_client = AzureFormRecognizerClient()
      cv_text = form_client.analyze_read(cv)[0]
      client = AzureBlobStorageClient()
      client.upload_file(cv_text, resume+".txt", "processed", "txt")
      

      llm_helper = LLMHelper(temperature=0, max_tokens=500)
      
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


            my_bar.progress(30, text="Impostazione analisi prompts")
            for index,prompt in enumerate(prompts):
                with open(os.path.join('prompts', 'profilo01', prompt["text"]), 'r', encoding='utf-8') as file:
                    prompt_text = file.read()
                #st.markdown(prompt["description"])
                # st.markdown(prompt_text)
                prompt['output'] = llm_helper.get_hr_completion(prompt_text.replace('{cv}', cv_text))
                progress = int(30 + 70 * (index + 1) / len(prompts))
                my_bar.progress(progress, text=f"Analisi attraversi prompt N. "+str(index+1))
                #st.markdown(output)
                time.sleep(3)
      
      elif profile == "Profilo n.2":
            st.error("Profilo non ancora implementato")
      elif profile == "Profilo n.3":
            st.error("Profilo non ancora implementato")
      else:
            st.error("Profilo non riconosciuto")
            return
      my_bar.progress(100,text="Analisi completata")
      time.sleep(1)
      my_bar.empty()

      data = ""
      for prompt in prompts:
        with st.expander(prompt["description"],expanded=False):
            st.markdown(prompt["output"])
            data += prompt["output"] + "\n\n"
      
      st.download_button(
      label="Scarica analisi come txt",
      data=data,
      file_name=profile+'_analisi.txt',
      mime='text/plain',
)
    except Exception as e:
        error_string = traceback.format_exc()
        st.error(error_string)
        
        # print(error_string)

        # output_debug.write(error_string)
        # final_debug_text = output_debug.getvalue()
        # output_debug.close()
        # st.download_button('Scarica il file per il debug', final_debug_text)


try:
    st.set_page_config(layout="wide")
    st.title("Analisi e Calcolo Punteggi per CV")
    profile = st.selectbox(
        "Profilo:", ("Profilo n.1", "Profilo n.2", "Profilo n.3"))
    uploaded_cv = st.file_uploader(
        "Caricare un CV (formato PDF)", type=['pdf'], key=1)

    st.title("Seleziona curriculum vitae")
    client = AzureBlobStorageClient()
    resumes = client.get_all_urls("resumes")
    resumes =[ x['file'] for x in resumes]
    resume = st.selectbox("Resume",resumes)
    

    # if uploaded_cv is not None:
    #     form_client = AzureFormRecognizerClient()
    #     results = form_client.analyze_read(uploaded_cv)
    #     cv = results[0]
    #     st.session_state["cv"] = cv
    #     st.success("Il file è stato caricato con successo")

    

    # if st.session_state.get("cv") is None:
    #   button = st.button(label="Inizio Analisi", disabled=True,on_click=valutazione, args=(profile,))
    # else:
    button = st.button(label="Inizio Analisi",on_click=valutazione, args=(profile,resume,))

     

except Exception as e:
    st.error(traceback.format_exc())
