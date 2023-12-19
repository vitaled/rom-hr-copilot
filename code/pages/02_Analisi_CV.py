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
from utilities.StreamlitHelper import StreamlitHelper


def reset(profile, resume):

    client = AzureBlobStorageClient()

    if not client.delete_blob("processed", resume+".txt"):
        st.success("CV non ancora processato")
        return

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
        for index, prompt in enumerate(prompts):
            client.delete_blob("analyzed", resume+"_"+prompt["text"])
    elif profile == "Profilo n.2":
        st.error("Profilo non ancora implementato")
    elif profile == "Profilo n.3":
        st.error("Profilo non ancora implementato")
    else:
        st.error("Profilo non riconosciuto")

    st.success("Reset completato")
    logger.info("Reset completato")
    return


def valutazione(profile, resume):
    try:
        client = AzureBlobStorageClient()
        my_bar = st.progress(0, text="Inizio Analisi")

        my_bar.progress(10, text="Recupero CV")
        cv = client.download_blob_to_bytes("resumes", resume)

        my_bar.progress(20, text="Estrazione Testo")
        form_client = AzureFormRecognizerClient()
        cv_text = form_client.analyze_read(cv)[0]
        client = AzureBlobStorageClient()
        client.upload_file(cv_text, resume+".txt", "processed", "txt")

        llm_helper = LLMHelper(
            temperature=st.session_state["temperature"], max_tokens=st.session_state["token_response"])

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
            for index, prompt in enumerate(prompts):
                output = client.download_blob_to_string(
                    "analyzed", resume+"_"+prompt["text"])
                if output is not None:
                    prompt["output"] = output
                else:
                    with open(os.path.join('prompts', 'profilo01', prompt["text"]), 'r', encoding='utf-8') as file:
                        prompt_text = file.read()
                    prompt['output'] = llm_helper.get_hr_completion(
                        prompt_text.replace('{cv}', cv_text))
                    progress = int(30 + 70 * (index + 1) / len(prompts))
                    my_bar.progress(progress, text=f"Analisi attraverso prompt N. "+str(index+1))

        elif profile == "Profilo n.2":
            st.error("Profilo non ancora implementato")
        elif profile == "Profilo n.3":
            st.error("Profilo non ancora implementato")
        else:
            st.error("Profilo non riconosciuto")
            return

        my_bar.progress(100, text="Analisi completata")
        #time.sleep(1)
        my_bar.empty()

        data = ""
        for prompt in prompts:
            with st.expander(prompt["description"], expanded=False):
                st.markdown(prompt["output"])
                data += prompt["output"] + "\n\n"
                client.upload_file(
                    data, resume+"_"+prompt["text"], "analyzed", "txt")

        st.download_button(
            label="Scarica analisi come txt",
            data=data,
            file_name=profile+'_analisi.txt',
            mime='text/plain',
        )
        st.button(label="Reset Analisi Precedente", on_click=reset, args=(profile, resume,))
    except Exception as e:
        error_string = traceback.format_exc()
        st.error(error_string)


try:
    st.set_page_config(layout="wide")
    StreamlitHelper.setup_session_state()
    StreamlitHelper.hide_footer()
    
    st.title("Analisi e Calcolo Punteggi per CV")
    st.markdown("### In questa pagina è possibile caricare un CV e ottenere una valutazione del CV rispetto a profili diversi")
    st.markdown("#### Seleziona profilo")
    profile = st.selectbox("Profilo:", ("Profilo n.1", "Profilo n.2", "Profilo n.3"))
    
    st.markdown("#### Seleziona curriculum vitae")
    client = AzureBlobStorageClient()
    resumes = client.get_all_urls("resumes")
    resumes = [x['file'] for x in resumes]
    resume = st.selectbox("Resumes", resumes)

    # Create a placeholder
    if st.button(label="Inizio Analisi"):
        # Call the function and display the output in the placeholder
        output = valutazione(profile, resume)
        st.write(output)
    
    StreamlitHelper.hide_footer()
except Exception as e:
    st.error(traceback.format_exc())
