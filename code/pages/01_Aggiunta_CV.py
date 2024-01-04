import streamlit as st
import traceback
from utilities.AzureBlobStorageClient import AzureBlobStorageClient
from utilities.StreamlitHelper import StreamlitHelper
from utilities.AzureCosmosDBClient import AzureCosmosDBClient
from utilities.AzureFormRecognizerClient import AzureFormRecognizerClient
import hashlib
import logging as logger

try:
    st.set_page_config(layout="wide")
    StreamlitHelper.setup_session_state()
    StreamlitHelper.hide_footer()
    client = AzureBlobStorageClient()
    cosmos_db = AzureCosmosDBClient()
    
    st.title("Aggiungi CV per un candidato")
    st.markdown("In questa pagina è possibile caricare nuovi candidati.")
    
    name = st.text_input("Nome")
    surname = st.text_input("Cognome")
    profiles = cosmos_db.get_profiles()
    profiles_description = [profile["profile_id"] for profile in profiles]
    multiselect = st.multiselect("Profili", profiles_description,max_selections=2)


    with st.expander("Caricare un nuovo CV", expanded=True):
        uploaded_cv = st.file_uploader("Caricamento Nuovo Documento", type=['txt', 'pdf'], key=1)

        if st.button("Carica CV", key=2):
            logger.info("Tentativo di creazione Candidato")

            candidates = list(cosmos_db.get_candidate_by_name_and_surname(name,surname))
            candidate = None
            if len(candidates) == 1:
                candidate = candidates[0]
            
            
                candidate["candidature"] = multiselect

                logger.info("Tentativo di caricamento CV")
                if uploaded_cv is None:
                    st.error("Devi selezionare un file prima di poterlo caricare!")
                else:
                    logger.info("Caricamento CV")
                    client = AzureBlobStorageClient()
                    cosmos_db = AzureCosmosDBClient()
                    form_client = AzureFormRecognizerClient()
                    # Calcolo hash del file
                    hash_md5 = hashlib.md5()
                    hash_md5.update()
                    file_hash = hash_md5.hexdigest()

                    # Caricamento file su Azure Blob Storage
                    logger.info("Caricamento file su Azure Blob Storage")
                    client.upload_file(uploaded_cv, f"{file_hash}.pdf","resumes", uploaded_cv.type)

                    # Estrazione testo da CV    
                    logger.info("Estrazione testo da CV")
                    cv_text = form_client.analyze_read(uploaded_cv.getvalue())[0]

                    # Caricamento CV su Azure Cosmos DB
                    logger.info("Caricamento CV su Azure Cosmos DB")
                    cosmos_db.put_resume({
                        "id": file_hash,
                        "name": uploaded_cv.name,
                        "type": uploaded_cv.type,
                        "size": uploaded_cv.size,
                        "text": cv_text,
                    })

                    
                    candidate["resume_id"] = file_hash

                    cosmos_db.put_candidate(candidate)

                    st.success("Il file è stato caricato con successo!")
            elif len(candidates) > 1:
                st.error("Nome ambiguo")
            else:
                st.error("Candidato non trovato")
    StreamlitHelper.hide_footer()
except Exception as e:
    st.error(traceback.format_exc())
