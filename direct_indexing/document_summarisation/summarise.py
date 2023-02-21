
import logging
from io import BytesIO
from urllib.request import urlopen

import docx2txt
import requests
from PyPDF2 import PdfReader

NOT_EXTRACTED = 'Not extractable'


def _download_files(url, format):
    """
    Function retrieves pdf files or word documents from internet
    :param url: url of the file
    :param format: format of the file
    """

    try:
        if 'pdf' in format:
            res = requests.get(url)
            byte_data = res.content
            return byte_data

        if 'msword' in format:
            res = urlopen(url)
            byte_data = res.read()
            return byte_data
        else:
            raise KeyError('Wrong file format!')
    except KeyError:
        raise KeyError('Wrong file format!')


def _extract_text(doc_bytes, doc_format):
    """
    Function extracts texts from either pdf or word documents
    """
    all_extracted_text = ""

    try:
        if 'pdf' in doc_format:
            # Extract text from pdf
            reader = PdfReader(BytesIO(doc_bytes))
            number_of_pages = len(reader.pages)
            for n in range(number_of_pages):
                page = reader.pages[n]
                all_extracted_text += page.extract_text()
            return all_extracted_text

        if 'msword' in doc_format:
            # extract text from ms word format
            return docx2txt.process(BytesIO(doc_bytes))
    except Exception:
        return NOT_EXTRACTED


def _extractive_summary(text, model):
    result = model(text, min_length=60)
    summarised_text = "".join(result)
    return summarised_text


def supported_doctype(doc_format):
    """
    Check if the document format is supported
    """
    if doc_format in ["application/pdf", "application/msword"]:
        return True
    return False


def summarise_document_content(doc_link, doc_format, model):
    """
    Download the content of the provided file
    Extract the text
    Summarise the text
    return the summary

    :param doc_link: the document link URL
    :param model: the summarisation model
    """
    try:
        byte_data = _download_files(doc_link, doc_format)
        text = _extract_text(byte_data, doc_format)
        if text == NOT_EXTRACTED:
            return NOT_EXTRACTED
        summary = _extractive_summary(text, model)
        return summary
    except KeyError as e:
        logging.error(f'_summarise_document_content:: Error summarising document:\n{e}')
        raise TypeError(f'Error summarising document:\n{e}')
