import os
import openai
from dotenv import load_dotenv
import logging
import re
import hashlib
from azure.identity import ManagedIdentityCredential

from langchain.llms import AzureOpenAI
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chains.llm import LLMChain
from langchain.chains.chat_vector_db.prompts import CONDENSE_QUESTION_PROMPT
from langchain.document_loaders.base import BaseLoader
from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import TokenTextSplitter, TextSplitter
from langchain.document_loaders.base import BaseLoader
from langchain.document_loaders import TextLoader
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from utilities.AzureFormRecognizerClient import AzureFormRecognizerClient
from utilities.AzureBlobStorageClient import AzureBlobStorageClient
from utilities.customprompt import PROMPT

import pandas as pd
import urllib
from fake_useragent import UserAgent


class LLMHelper:
    def __init__(self,
                 document_loaders: BaseLoader = None,
                 llm: AzureOpenAI = None,
                 temperature: float = None,
                 max_tokens: int = None,
                 pdf_parser: AzureFormRecognizerClient = None,
                 blob_client: AzureBlobStorageClient = None,
                 ):

        load_dotenv()

        openai.api_type = os.getenv("API_TYPE", "azure")

        if openai.api_type == "azure":
            openai.api_key = os.getenv("OPENAI_API_KEY")
        elif openai.api_type == "azure_ad":
            openai.api_key = self._get_token(
                os.getenv("APP_CONTAINER_CLIENT_ID"))

        openai.api_base = os.getenv('OPENAI_API_BASE')
        openai.api_version = "2023-03-15-preview"

        # Azure OpenAI settings
        self.api_base = openai.api_base
        self.api_version = openai.api_version
        self.deployment_name: str = os.getenv("OPENAI_ENGINE", os.getenv("OPENAI_ENGINES", "text-davinci-003"))
        self.temperature: float = float(
            os.getenv("OPENAI_TEMPERATURE", 0.7)) if temperature is None else temperature
        self.max_tokens: int = int(
            os.getenv("OPENAI_MAX_TOKENS", -1)) if max_tokens is None else max_tokens
        self.document_loaders: BaseLoader = WebBaseLoader if document_loaders is None else document_loaders
        self.llm: ChatOpenAI = ChatOpenAI(model_name=self.deployment_name, engine=self.deployment_name, temperature=self.temperature,
                                          max_tokens=self.max_tokens, request_timeout=180, openai_api_key=openai.api_key) if llm is None else llm
        self.pdf_parser: AzureFormRecognizerClient = AzureFormRecognizerClient(
        ) if pdf_parser is None else pdf_parser
        self.blob_client: AzureBlobStorageClient = AzureBlobStorageClient(
        ) if blob_client is None else blob_client

    def get_hr_completion(self, prompt: str):
        messages = [
            SystemMessage(content="Sei l'assistente digitale per il Recruitment del Comune di Roma. Aiuti nelle analisi di CV e a calcolare i punteggi per determinare la classifica dei candidati."),
            HumanMessage(content=prompt)]
        return self.llm(messages).content

    def get_qa_completion(self, prompt: str):
        messages = [
            SystemMessage(content="Sei l'assistente digitale per il Recruitment del Comune di Roma. Ricevi domande su CV che ti vengono forniti e aiuti nell'estrazione di informazioni dal testo rispetto alle domande che ti vengono fatte."),
            HumanMessage(content=prompt)]
        return self.llm(messages).content

    def _get_token(self, client_id):
        azure_credential = ManagedIdentityCredential(client_id=client_id)
        openai_token = azure_credential.get_token(
            "https://cognitiveservices.azure.com/.default")
        return openai_token.token
