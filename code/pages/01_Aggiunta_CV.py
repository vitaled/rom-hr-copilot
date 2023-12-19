import streamlit as st
from os import path
import mimetypes
import traceback
from utilities.LLMHelper import LLMHelper
from utilities.AzureBlobStorageClient import AzureBlobStorageClient
from utilities.StreamlitHelper import StreamlitHelper

try:
    st.set_page_config(layout="wide")
    StreamlitHelper.setup_session_state()
    StreamlitHelper.hide_footer()
    
    st.title("Aggiunta CV e Job Description")
    st.markdown("In questa pagina è possibile caricare nuovi CV. I documenti verranno caricati su Azure Blob Storage.")    
    
    with st.expander("Caricare un nuovo CV", expanded=True):
        uploaded_cv = st.file_uploader("Caricamento Nuovo Documento", type=['txt', 'pdf'], key=1)
        if uploaded_cv is not None:
            client = AzureBlobStorageClient()
            client.upload_file(uploaded_cv, uploaded_cv.name, "resumes", uploaded_cv.type)
            st.success("Il file è stato caricato con successo su Azure Blob Storage!")

    StreamlitHelper.hide_footer()
except Exception as e:
    st.error(traceback.format_exc())
