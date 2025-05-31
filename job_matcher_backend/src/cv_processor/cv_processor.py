import os
from io import BytesIO

from .extractor.pdf_extractor import PDFExtractor
from .extractor.docx_extractor import DOCXExtractor
from ..clients.openai_embedding_client import OpenAIEmbeddingClient
from ..preprocessor.preprocessor import TextPreprocessor

class CVProcessor:
    """Process CV files to extract text, preprocess it and generate embeddings."""

    @staticmethod
    def process_file(file_stream: BytesIO, preprocessor: TextPreprocessor, 
                    embedding_client: OpenAIEmbeddingClient):
        """Process a CV file and return its embedding"""
        try:
            raw_text = CVProcessor.extract_text(file_stream)

            preprocessed_text = preprocessor.preprocess_cv(raw_text)

            embedding = embedding_client.create(preprocessed_text).data[0].embedding
            
            return embedding
        finally:
            file_stream.close()
    
    @staticmethod
    def extract_text(file_stream: BytesIO):
        """Extract text from a CV file"""
        file_type = CVProcessor._detect_file_type(file_stream)
        if file_type == 'pdf':
            extractor = PDFExtractor(file_stream)
        elif file_type == 'docx':
            extractor = DOCXExtractor(file_stream)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        return extractor.extract_text()

    @staticmethod
    def _detect_file_type(file_stream: BytesIO):
        """ Detect the file extension based on the first bytes """
        file_stream.seek(0)  
        file_signature = file_stream.read(4)
        file_stream.seek(0)
        
        if file_signature[:4] == b"%PDF":
            return "pdf"
        elif file_signature[:2] == b'PK':
            return "docx"
        else:
            raise ValueError("Unsupported file type")

if __name__=="__main__":
    embedding_client=OpenAIEmbeddingClient()
    preprocessor=TextPreprocessor()

    embedding=CVProcessor.process_file(open("sample_data/BiticaSebastianCV.pdf","rb"), embedding_client, preprocessor)
    print(embedding)