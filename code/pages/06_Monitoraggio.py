import streamlit as st
from utilities.StreamlitHelper import StreamlitHelper
import traceback
from utilities.AzureCosmosDBClient import AzureCosmosDBClient
from dotenv import load_dotenv
load_dotenv()

FIELDS = ('id', 'run_id', 'starting_time',
          'ending_time', 'status', 'file_name')


try:
    st.set_page_config(layout="wide")
    StreamlitHelper.hide_footer()

    cosmos_client = AzureCosmosDBClient()
    st.markdown("# Monitoraggio")
    st.markdown(
        "## In questa pagina è possibile monitorare i processi di caricamento dei CV.")
    st.markdown(
        "### I processi sono divisi per stato: running, completed, failed, pending")
    select = st.selectbox("status", ["completed",
                                     "running",
                                     "failed",
                                     "pending"], index=1, key="upload_monitorigìng")
    if select:
        data = cosmos_client.get_upload_runs_by_status(select)

    st.dataframe(data, column_order=FIELDS,use_container_width=True)

    st.markdown(
        "## In questa pagina è possibile monitorare i processi di analisi dei CV.")
    st.markdown(
        "### I processi sono divisi per stato: running, completed, failed, pending")
    select = st.selectbox("status", ["completed",
                                     "running",
                                     "failed",
                                     "pending"], index=1, key="analysis_monitoring")
    if select:
        data = cosmos_client.get_analyses_runs_by_status(select)
    st.dataframe(data, column_order=FIELDS,use_container_width=True)
except Exception as e:
    st.error(e)
    st.error(traceback.format_exc())
