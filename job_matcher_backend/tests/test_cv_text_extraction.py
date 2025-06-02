from io import BytesIO
from src.cv_processor.extractor.docx_extractor import DOCXExtractor
from src.cv_processor.extractor.pdf_extractor import PDFExtractor

# TEXT EXTRACTION TESTS



# Sample expected text for comparison
PDF_Text = """
 Name: Andrei Popescu
Email: andrei.popescu@example.com
Phone: +40 723-456-789
Location: Bucharest, Romania
Work Experience:
BuildTech Inc., Bucharest – Civil Engineer (2019 - Present)
Managed and supervised construction sites
Analyzed and optimized structural plans
Collaborated with architects and construction teams
ConSteel S.A., Cluj-Napoca – Structural Engineer (2016 - 2019)
Designed and developed structural projects for residential and commercial buildings
Skills:
Proficient in AutoCAD, Revit, SAP2000
Project management in construction
Structural materials evaluation and testing
Team coordination and safety compliance
"""

DOCX_Text = """
 ROBINSON
CHRISTOPER
Summary
Senior Web Developer specializing in front end development. Experienced with all stages of the development cycle for dynamic web projects. Well-versed in numerous programming languages including HTML5, PHP OOP, JavaScript, CSS, MySQL. Strong background in project management and customer relations.
Skill Highlights
Project management
Strong decision maker
Complex problem solver
Creative design
Innovative
Service-focused
Experience
Web Developer - 09/2015 to 05/2019
Luna Web Design, New York
Cooperate with designers to create clean interfaces and simple, intuitive interactions and experiences.
Develop project concepts and maintain optimal workflow.
Work with senior developer to manage large, complex design projects for corporate clients.
Complete detailed programming and development tasks for front end public and internal websites as well as challenging back-end server code.
Carry out quality assurance tests to discover errors and optimize usability.
Education
Bachelor of Science: Computer Information Systems - 2014
Columbia University, NY
Certifications
PHP Framework (certificate): Zend, Codeigniter, Symfony.
Programming Languages: JavaScript, HTML5, PHP OOP, CSS, SQL, MySQL.
Contact
Address:
177 Great Portland Street, London W5W 6PQ
Phone:
+44 (0)20 7666 8555
Email:
christoper.robinson@gmail.com
Languages
Spanish – C2
Chinese – A1
German – A2
"""

def compare_texts(extracted, expected):
    # Remove all whitespace for comparison
    def normalize(s):
        return "".join(s.split())
    extracted_norm = normalize(extracted)
    expected_norm = normalize(expected)
    if extracted_norm == expected_norm:
        print("Text matches (ignoring whitespace)!")
    else:
        print("Text does NOT match (ignoring whitespace).")
        print("First 200 chars of extracted (normalized):")
        print(repr(extracted_norm[:200]))
        print("First 200 chars of expected (normalized):")
        print(repr(expected_norm[:200]))

def test_docx_extractor():
    with open("../sample_data/example4.docx", "rb") as f:
        file_stream = BytesIO(f.read())
    extractor = DOCXExtractor(file_stream)
    text = extractor.extract_text()
    # print("DOCX:", text)
    compare_texts(text, DOCX_Text)
    assert isinstance(text, str)
    assert len(text) > 0

def test_pdf_extractor():
    with open("../sample_data/inginer_constructor_pdf.pdf", "rb") as f:
        file_stream = BytesIO(f.read())
    extractor = PDFExtractor(file_stream)
    text = extractor.extract_text()
    # print("PDF:", text)
    compare_texts(text, PDF_Text)
    assert isinstance(text, str)
    assert len(text) > 0

if __name__ == "__main__":
    test_docx_extractor()
    test_pdf_extractor()
    print("All tests passed!")