import traceback
from utilities.AzureCosmosDBClient import AzureCosmosDBClient
from utilities.StreamlitHelper import StreamlitHelper
import streamlit as st

def delete(candidate_id):
    try:
        cosmos_db = AzureCosmosDBClient()
        cosmos_db.delete_candidate_by_id(candidate_id)
        st.success("Candidato eliminato con successo")
    except:
        st.error("Errore durante l'eliminazione del candidato")    

try:
    st.set_page_config(layout="wide")
    StreamlitHelper.setup_session_state()
    StreamlitHelper.hide_footer()
    cosmos_db = AzureCosmosDBClient()
    candidates = cosmos_db.get_candidates()

    colms = st.columns((1, 1, 1,1,1))
    fields = ['CodiceFiscale',
              'Nome',
              'Cognome',
              'CV Caricato',
              ''
              ]
    for col, field_name in zip(colms, fields):
        # header
        col.write(field_name)

    for candidate in candidates:
        if "candidature" in candidate:
            profile = candidate["candidature"][0]
            col1,col2,col3,col4,col5 = st.columns((1, 1, 1,1,1))
            col1.write(candidate[profile]['Codice Fiscale'])
            col2.write(candidate[profile]['Nome'])
            col3.write(candidate[profile]['Cognome'])
            col4.write("Sì" if 'resume_id' in candidate else "No")
            button_phold = col5.empty()  # create a placeholder
            col5.button("elimina",disabled=False, on_click=delete, args=(candidate['id'],), key="delete_"+candidate['id'])

            

except Exception as e:
    st.error(traceback.format_exc())
