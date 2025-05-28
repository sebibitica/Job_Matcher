import os
from io import BytesIO

from .extractor.pdf_extractor import PDFExtractor
from .extractor.docx_extractor import DOCXExtractor
from ..clients.openai_embedding_client import OpenAIEmbeddingClient

class CVProcessor:
    def __init__(self, file_stream: BytesIO, embedding_client: OpenAIEmbeddingClient):
        """ Initialize the CVProcessor with a byte stream and embedding client """
        self.embedding_client = embedding_client
        self.file_stream = file_stream

        # Detect file extension from the byte stream
        file_extension = self._detect_file_extension()

        if file_extension == '.pdf':
            self.extractor = PDFExtractor(self.file_stream)
        elif file_extension == '.docx':
            self.extractor = DOCXExtractor(self.file_stream)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

    def process(self):
        """ Process the CV to generate its embedding """
        text = self.extractor.extract_text()
        response = self.embedding_client.create(text)
        return response.data[0].embedding

    def _detect_file_extension(self):
        """ Detect the file extension based on the bytes """
        # Read the first few bytes to check the type of the file
        self.file_stream.seek(0)  
        file_signature = self.file_stream.read(4)

        # Reset the stream position
        self.file_stream.seek(0)
        
        if file_signature[:4] == b"%PDF":  # PDF
            return ".pdf"
        elif file_signature[:2] == b'PK':  # DOCX (ZIP format)
            return ".docx"
        else:
            raise ValueError("Unsupported file type")

if __name__=="__main__":
    embedding_client=OpenAIEmbeddingClient()
    cv_processor=CVProcessor(open("sample_data/example2.pdf","rb"), embedding_client)
    print(cv_processor.process())