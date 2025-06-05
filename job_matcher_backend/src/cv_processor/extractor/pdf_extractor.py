import logging
import os
import zipfile
import json
from io import BytesIO

from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.io.cloud_asset import CloudAsset
from adobe.pdfservices.operation.io.stream_asset import StreamAsset
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.pdfjobs.jobs.extract_pdf_job import ExtractPDFJob
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_element_type import ExtractElementType
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_pdf_params import ExtractPDFParams
from adobe.pdfservices.operation.pdfjobs.result.extract_pdf_result import ExtractPDFResult

adobe_client_id = os.getenv('ADOBE_PDF_SERVICES_CLIENT_ID')
adobe_client_secret = os.getenv('ADOBE_PDF_SERVICES_CLIENT_SECRET')


class PDFExtractor:
    """Extract text from a PDF file stream using Adobe PDF Services."""
    def __init__(self, file_stream: BytesIO):
        if not file_stream:
            raise ValueError("file_stream must be provided.")
        self.file_stream = file_stream

        credentials = ServicePrincipalCredentials(
            client_id=adobe_client_id,
            client_secret=adobe_client_secret
        )

        self.pdf_services = PDFServices(credentials=credentials)


    def extract_text(self) -> str:
        """Extract and return text from the PDF file."""
        try:
            input_stream = self.file_stream

            input_asset = self.pdf_services.upload(input_stream=input_stream, mime_type=PDFServicesMediaType.PDF)

            extract_pdf_params = ExtractPDFParams(
                elements_to_extract=[ExtractElementType.TEXT],
            )

            extract_pdf_job = ExtractPDFJob(input_asset=input_asset, extract_pdf_params=extract_pdf_params)
            
            location = self.pdf_services.submit(extract_pdf_job)

            # get job result (ZIP file) as stream
            pdf_services_response = self.pdf_services.get_job_result(location, ExtractPDFResult)
            result_asset: CloudAsset = pdf_services_response.get_result().get_resource()
            stream_asset: StreamAsset = self.pdf_services.get_content(result_asset)

            extracted_text = self.extract_text_from_stream(stream_asset.get_input_stream())

            return extracted_text

        except (ServiceApiException, ServiceUsageException, SdkException) as e:
            logging.exception(f'Exception encountered while executing operation: {e}')
            return ""

    @staticmethod
    def extract_text_from_stream(zip_stream: bytes) -> str:
        """Extract text from the structuredData.json inside the ZIP stream."""
        with zipfile.ZipFile(BytesIO(zip_stream), 'r') as zip_ref:
            for file_name in zip_ref.namelist():
                if "structuredData.json" in file_name:
                    with zip_ref.open(file_name) as json_file:
                        data = json.load(json_file)
                        return PDFExtractor.extract_text_from_json(data)
        return "structuredData.json not found in the ZIP file."

    @staticmethod
    def extract_text_from_json(data: dict) -> str:
        """Extract text elements from the structuredData.json content."""
        extracted_text = []
        if 'elements' in data:
            for element in data['elements']:
                if 'Text' in element:
                    extracted_text.append(element['Text'])
        return '\n'.join(extracted_text)


if __name__ == "__main__":
    file = open("sample_data/example1.pdf", "rb")
    extractor = PDFExtractor(file)

    extracted_text = extractor.extract_text()
    print(extracted_text)