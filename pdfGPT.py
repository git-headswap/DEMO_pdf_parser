from openai import OpenAI
import streamlit as st
from pdf2image import convert_from_bytes
import pytesseract
import requests

with st.sidebar:
    API_KEY = st.text_input("Enter your API key")

if API_KEY:
    with st.sidebar:
        model = st.radio("Model", ["gpt-4-1106-preview", "gpt-4-1106-vision-preview", "gpt-4", "gpt-4-32k", "gpt-3.5-turbo-1106"], index=4)

model_price = {
    "gpt-4-1106-preview": {"input":0.01/1000, "output": 0.03/1000},
    "gpt-4-1106-vision-preview": {"input":0.01/1000, "output": 0.03/1000},
    "gpt-4-0613": {"input":0.03/1000, "output": 0.06/1000},
    "gpt-4-32k": {"input":0.06/1000, "output": 0.12/1000},
    "gpt-3.5-turbo-1106": {"input":0.001/1000, "output": 0.002/1000},
}

def parsePDF(message, model, info_to_extract):
    global model_price, API_KEY

    payload = {
        "model": model,
        "messages": [{"role": "system", "content": f"You will receive an ocr PDF, your job is to extract the following information: {info_to_extract} as JSON. If the information is not provided please write N/A."},
                {"role": "user", "content": f"Here is the pdf ocr: {message}"}],
        "max_tokens": 256,
        "temperature": 0,
        
    }

    headers = {
        "api_key_2": API_KEY
    }

    response = requests.post("https://api.headswap.com/demo", headers=headers, json=payload)

    st.header("Extracted info")
    st.write(response.json())


@st.cache_data
def ocrPDF(pdf_file):
    # Convert PDF to images
    pdf_data = pdf_file.read()
    pages = convert_from_bytes(pdf_data, 100)  # 500 is the DPI (adjust as needed)

    # Perform OCR on each page
    text = ''
    for page in pages:
        text += pytesseract.image_to_string(page, lang='eng')

    return text

if API_KEY:
    st.header("PDF parsing demo")

    info_to_extract = st.text_area("Info to extract", "Policy number, type of Policy, insurance, company, name of policy holder, start/end of Policy and birth date")

    pdf_file = st.file_uploader("Upload a pdf")

    if pdf_file:
        text = ocrPDF(pdf_file)
        parsePDF(text, model, info_to_extract)