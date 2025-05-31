import docx2txt
from io import BytesIO


class DOCXExtractor:
    """Extract text from a DOCX file stream."""
    def __init__(self, file_stream: BytesIO):
        if not file_stream:
            raise ValueError("file_stream must be provided.")
        self.file_stream = file_stream

    def extract_text(self) -> str:
        """Extract and deduplicate text from the DOCX file."""
        text = docx2txt.process(self.file_stream)

        lines = text.splitlines()
        unique_lines = []
        for line in lines:
            if line.strip() and line not in unique_lines:
                unique_lines.append(line)

        return "\n".join(unique_lines)
    
if __name__ == "__main__":
    file = open("sample_data/example4.docx", "rb")
    extractor = DOCXExtractor(file)

    extracted_text = extractor.extract_text()
    print(extracted_text)
