from azure.core.credentials import AzureKeyCredential
import os
from dotenv import load_dotenv
from azure.identity import ManagedIdentityCredential

from azure.ai.documentintelligence import DocumentIntelligenceClient


class AzureFormRecognizerClient:
    def __init__(self, form_recognizer_endpoint: str = None, form_recognizer_key: str = None):

        load_dotenv()

        self.pages_per_embeddings = 20
        self.section_to_exclude = ['footnote','pageFooter', 'pageNumber']

        self.form_recognizer_endpoint: str = form_recognizer_endpoint if form_recognizer_endpoint else os.getenv(
            'FORM_RECOGNIZER_ENDPOINT')
        self.form_recognizer_key: str = form_recognizer_key if form_recognizer_key else os.getenv(
            'FORM_RECOGNIZER_KEY')

    def _get_credential(self):
        if self.form_recognizer_key is None:
            return ManagedIdentityCredential(
                client_id=os.getenv("APP_CONTAINER_CLIENT_ID"))
        else:
            return AzureKeyCredential(self.form_recognizer_key)

    def analyze_read(self, formUrl):
        document_analysis_client = DocumentAnalysisClient(
            endpoint=self.form_recognizer_endpoint, credential=self._get_credential()
        )

        poller = document_analysis_client.begin_analyze_document_from_url(
            "prebuilt-layout", formUrl)
        layout = poller.result()

        results = []
        page_result = ''
        for p in layout.paragraphs:
            page_number = p.bounding_regions[0].page_number
            output_file_id = int((page_number - 1) / self.pages_per_embeddings)

            if len(results) < output_file_id + 1:
                results.append('')

            if p.role not in self.section_to_exclude:
                results[output_file_id] += f"{p.content}\n"

        for t in layout.tables:
            page_number = t.bounding_regions[0].page_number
            output_file_id = int((page_number - 1) / self.pages_per_embeddings)

            if len(results) < output_file_id + 1:
                results.append('')
            previous_cell_row = 0
            rowcontent = '| '
            tablecontent = ''
            for c in t.cells:
                if c.row_index == previous_cell_row:
                    rowcontent += c.content + " | "
                else:
                    tablecontent += rowcontent + "\n"
                    rowcontent = '|'
                    rowcontent += c.content + " | "
                    previous_cell_row += 1
            results[output_file_id] += f"{tablecontent}|"
        return results

    def analyze_read(self, pdf: bytes):

        document_analysis_client = DocumentIntelligenceClient(
            endpoint=self.form_recognizer_endpoint, credential=self._get_credential())
#"prebuilt-layout"
        poller = document_analysis_client.begin_analyze_document("prebuilt-layout",analyze_request=pdf,content_type="application/pdf")
        layout = poller.result()
        results = []
        page_result = ''
        for p in layout.paragraphs:
            page_number = p.bounding_regions[0].page_number
            output_file_id = int((page_number - 1) / self.pages_per_embeddings)

            if len(results) < output_file_id + 1:
                results.append('')

            if p.role not in self.section_to_exclude:
                results[output_file_id] += f"{p.content}\n"

        for t in layout.tables:
            page_number = t.bounding_regions[0].page_number
            output_file_id = int((page_number - 1) / self.pages_per_embeddings)

            if len(results) < output_file_id + 1:
                results.append('')
            previous_cell_row = 0
            rowcontent = '| '
            tablecontent = ''
            for c in t.cells:
                if c.row_index == previous_cell_row:
                    rowcontent += c.content + " | "
                else:
                    tablecontent += rowcontent + "\n"
                    rowcontent = '|'
                    rowcontent += c.content + " | "
                    previous_cell_row += 1
            results[output_file_id] += f"{tablecontent}|"
        return results
