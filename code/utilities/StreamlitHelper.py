import os
import openai
import logging
import re
import streamlit as st

class StreamlitHelper:
    @staticmethod
    def hide_footer():
        hide_streamlit_style = """
                    <style>
                    #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                    </style>
          
                    """
        
        st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    @staticmethod
    def clear_session_state():
        session_state = st.session_state
        for key in session_state.keys():
            session_state[key] = None
    
    @staticmethod
    def setup_session_state():
        if not  st.session_state.get("token_response"):
            st.session_state["token_response"]= 1000
        if not st.session_state.get("temperature"):
            st.session_state["temperature"] = 0.7
