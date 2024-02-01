
import warnings
warnings.filterwarnings("ignore")

from adobe.pdfservices.operation.auth.credentials import Credentials
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.execution_context import ExecutionContext
from adobe.pdfservices.operation.io.file_ref import FileRef
from adobe.pdfservices.operation.pdfops.extract_pdf_operation import ExtractPDFOperation
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_pdf_options import ExtractPDFOptions
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_element_type import ExtractElementType
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_renditions_element_type import ExtractRenditionsElementType 
import os.path
import zipfile
import json
import os
import shutil


class StructureExtractor:

    def __init__(self):
        credentials_builder = Credentials.service_principal_credentials_builder()
        adobe_id_key = input("Please insert adobe_id key : ")
        credentials_builder = credentials_builder.with_client_id(adobe_id_key)
        adobe_secret_key = input("Please insert adobe_id key : ")
        credentials_builder = credentials_builder.with_client_secret(adobe_secret_key).build()
        self.execution_context = ExecutionContext.create(credentials_builder)
        self.extract_pdf_operation = ExtractPDFOperation.create_new()
    
    def extract_structure(self, file_path):
        path = os.path.dirname(file_path)
        file_name = os.path.basename(file_path).replace(".pdf", "")
        save_path = os.path.join(path, "json")
        os.makedirs(save_path, exist_ok=True)
        file_json = os.path.join(save_path, file_name + ".json")
        save_file = os.path.join(save_path, file_name + ".zip")
        if os.path.exists(save_file):
            os.remove(save_file)
        source = FileRef.create_from_local_file(file_path)
        self.extract_pdf_operation.set_input(source)
        extract_pdf_options = ExtractPDFOptions.builder() \
            .with_elements_to_extract([ExtractElementType.TEXT, ExtractElementType.TABLES]) \
            .with_elements_to_extract_renditions([ExtractRenditionsElementType.TABLES, ExtractRenditionsElementType.FIGURES]) \
            .with_get_char_info(True) \
            .with_include_styling_info(True) \
            .build()
        self.extract_pdf_operation.set_options(extract_pdf_options)

        result = self.extract_pdf_operation.execute(self.execution_context)
        result.save_as(save_file)
        shutil.unpack_archive(save_file, extract_dir=os.path.join(save_path, file_name))
        os.remove(save_file)
        shutil.move(os.path.join(save_path, file_name, "structuredData.json"), file_json)
        return file_json
