"""
File ingestion module using the Unstructured library and pytesseract OCR.

This module provides functionality to ingest PDF and DOC files, extracting text,
tables, and images as unstructured document elements.
"""

import unstructured_pytesseract
from unstructured.partition import pdf, doc
import json
# import configparser
# config = configparser.ConfigParser()
# config.read("agentic_ai_docproc\config.ini")
# tesseract_path = config["OCR"]["tesseract_path"]
# Configure Tesseract OCR path
# if tesseract_path:
#     unstructured_pytesseract.pytesseract.tesseract_cmd = r"C:\Users\rmahesh668\Documents\Langchain\tesseract\tesseract.exe"
unstructured_pytesseract.pytesseract.tesseract_cmd = r"C:\Users\rmahesh668\Documents\Langchain\tesseract\tesseract.exe"
class IngestFile:
    """
    Class for ingesting files and converting them into unstructured document elements.

    Attributes:
        file_path (str): Path to the file to ingest.
    """

    def __init__(self, file_path):
        """
        Initialize the IngestFile instance.

        Args:
            file_path (str): Path to the input file (PDF or DOC).
        """
        self.file_path = file_path

    def get_data(self):
        """
        Partition the file based on its type.

        Returns:
            list: List of unstructured document elements.
        """
        if self.file_path.endswith('.pdf'):
            return self.__partition_pdf(self.file_path)
        elif self.file_path.endswith('.doc'):
            return self.__partition_doc(self.file_path)

    def __partition_pdf(self, file_path):
        """
        Partition a PDF file into unstructured elements.

        Args:
            file_path (str): Path to the PDF file.

        Returns:
            list: List of document elements extracted from the PDF.
        """
        return pdf.partition_pdf(
            filename=file_path,
            infer_table_structure=True,
            extract_image_block_types=['Image'],
            extract_image_block_to_payload=True,
            strategy="fast"
        )

    def __partition_doc(self, file_path):
        """
        Partition a DOC file into unstructured elements.

        Args:
            file_path (str): Path to the DOC file.

        Returns:
            list: List of document elements extracted from the DOC.
        """
        return doc.partition_doc(filename=file_path)


def ingest_file(file_path):
    """
    Convenience function to ingest a file and return document elements.

    Args:
        file_path (str): Path to the file to ingest.

    Returns:
        list: List of document elements.

    Raises:
        Exception: Re-raises any exception encountered during ingestion.
    """
    try:
        ingest = IngestFile(file_path)
        docs = ingest.get_data()
        return docs
    except Exception as e:
        print(f"Error in file path {file_path}")
        raise e


if __name__ == '__main__':
    print(ingest_file(r'test_data\functionalsample.pdf'))