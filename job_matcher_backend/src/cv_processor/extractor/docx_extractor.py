import docx2txt

class DOCXExtractor:
    def __init__(self, file_path: str):
        self.file_path = file_path
    def extract_text(self) -> str:
        text = docx2txt.process(self.file_path)

        lines = text.splitlines()
        
        unique_lines = []
        for line in lines:
            if line.strip() and line not in unique_lines:
                unique_lines.append(line)
        
        cleaned_text = "\n".join(unique_lines)
        return cleaned_text


if __name__ == "__main__":
    extractor = DOCXExtractor("sample_data/example5.docx")

    extracted_text = extractor.extract_text()
    print(extracted_text)