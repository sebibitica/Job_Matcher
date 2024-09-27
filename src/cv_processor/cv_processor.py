import os

from extractor.pdf_extractor import PDFExtractor
from extractor.docx_extractor import DOCXExtractor

class CVProcessor:
    def __init__(self, file_path):
        # Determine the extractor based on file extension
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension == '.pdf':
            self.extractor = PDFExtractor(file_path)
        elif file_extension == '.docx':
            self.extractor = DOCXExtractor(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    def process(self):
        text=self.extractor.extract_text()
        print(text)

if __name__=="__main__":
    cv_processor=CVProcessor("sample_data/example.pdf")
    cv_processor.process()