from transformers import pipeline
import requests
import re
import os
from io import BytesIO
from PyPDF2 import PdfReader


def download_files(url):
    """
    Function retrieves files from internet
    Returns: byte data and filename

    """
    res = requests.get(url)
    byte_data = res.content
    d = res.headers["content-disposition"]
    # Extract filename from header
    fname = re.findall("filename=(.+)", d)[0]

    return byte_data, fname


def extract_text(doc_bytes):
    """
    Function extracts texts from the pdf files
    """
    all_extracted_text = ""
    # Extract text from pdf
    reader = PdfReader(BytesIO(doc_bytes))
    number_of_pages = len(reader.pages)
    for n in range(number_of_pages):
        page = reader.pages[n]
        text = page.extract_text()
        all_extracted_text += text

    return all_extracted_text


def summarize_text(text):
    """
    Fucntion summarizes texts extracted from each document
    """
    chunk_size = 500
    # Break texts into chunks of 500 words
    chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]
    # Summizer might take a while to process all the text on a cpu
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    # pass in the chunks of texts to the summarization model
    res = summarizer(chunks, min_length=30, max_length=50, do_sample=False)
    # Append all different summaries into one
    document_summary = " ".join([summary["summary_text"] for summary in res])
    return document_summary


def summariez(doc_link):
    byte_data, fname = download_files(doc_link)
    text = extract_text(byte_data)
    summary = summarize_text(text)
    return summary, fname


def index_summaries(data):
    if "document-link" in data:
        if type(data["document-link"]):
            data["document-link"] = [data["document-link"]]  # ensure it is a list
        for dl in data["document-link"]:
            summarized_text, fname = summariez(dl)
            Solr.add(
                [
                    {
                        "id": fname,
                        "document_summary": summarized_text,
                    }
                ]
            )
