import os
import sys

from .extractor.pdf_extractor import PDFExtractor
from .extractor.docx_extractor import DOCXExtractor
from ..clients.openai_embedding_client import OpenAIEmbeddingClient

class CVProcessor:
    def __init__(self, file_path, embedding_client):
        self.embedding_client = embedding_client
        # Determine the extractor based on file extension
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension == '.pdf':
            self.extractor = PDFExtractor(file_path)
        elif file_extension == '.docx':
            self.extractor = DOCXExtractor(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    def process(self):
        print("Extracting text...")
        text=self.extractor.extract_text()
        print("Processing text...")
        response=self.embedding_client.create(text)
        return response.data[0].embedding

if __name__=="__main__":
    embedding_client=OpenAIEmbeddingClient()
    cv_processor=CVProcessor("sample_data/example4.docx", embedding_client)
    cv_processor.process()