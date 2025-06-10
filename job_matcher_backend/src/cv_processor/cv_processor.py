import asyncio
from io import BytesIO

from .extractor.pdf_extractor import PDFExtractor
from .extractor.docx_extractor import DOCXExtractor
from ..clients.openai_embedding_client import OpenAIEmbeddingClient
from ..preprocessor.preprocessor import TextPreprocessor
from ..user_profile.profile_structurer.profile_structurer import ProfileStructurer

class CVProcessor:
    """Process CV files to extract text, preprocess it and generate embeddings."""

    @staticmethod
    async def process_file(file_stream: BytesIO, preprocessor: TextPreprocessor, 
                    embedding_client: OpenAIEmbeddingClient):
        """Process a CV file and return its embedding"""
        try:
            raw_text = await asyncio.to_thread(CVProcessor.extract_text, file_stream)

            preprocessed_text = await preprocessor.preprocess_cv(raw_text)

            response_embedding = await embedding_client.create(preprocessed_text)

            embedding = response_embedding.data[0].embedding
            
            return embedding
        finally:
            file_stream.close()
    
    @staticmethod
    async def process_file_with_structure(file_stream: BytesIO, preprocessor: TextPreprocessor, 
                    embedding_client: OpenAIEmbeddingClient, profile_structurer: ProfileStructurer):
        """Process a CV file and return its embedding"""
        try:
            raw_text = await asyncio.to_thread(CVProcessor.extract_text, file_stream)

            structured_profile_str = await profile_structurer.structure_profile(raw_text)

            import json
            try:
                structured_profile = json.loads(structured_profile_str)
            except Exception as e:
                raise ValueError(f"Failed to parse structured profile JSON from GPT: {e}")

            preprocessed_text = await preprocessor.preprocess_cv(raw_text)

            response_embedding = await embedding_client.create(preprocessed_text)

            embedding = response_embedding.data[0].embedding
            
            return embedding, structured_profile
        except Exception as e:
            raise ValueError(f"Failed to process CV file: {e}")
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