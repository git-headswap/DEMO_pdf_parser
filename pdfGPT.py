from openai import OpenAI
import streamlit as st
from pdf2image import convert_from_bytes
import pytesseract
import requests
import json
import tiktoken

st.set_page_config(page_title="Headswap Demo", page_icon="static/logo.png", layout="wide")

tab1, tab2 = st.tabs(["PDF Parsing", "Token Calculator"])

@st.cache_data
def autoGPT(message, info_to_extract, API_KEY, model="gpt-3.5-turbo-1106"):
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": f"You will receive an ocr PDF, your job is to extract the following information: {info_to_extract} as JSON. If the information is not provided please write N/A."},
                {"role": "user", "content": f"Here is the pdf ocr: {message}"}],
        "max_tokens": 2048,
        "temperature": 0,
        
    }

    headers = {
        "api_key_2": API_KEY
    }

    response = requests.post("https://api.headswap.com/demo", headers=headers, json=payload)

    response = response.json()

    st.header("Extracted info")

    try:
        jsonObj = json.loads(response["text"])
    except:
        jsonObj = response["text"]
    
    st.write(jsonObj)

    st.header("Time")
    st.write(f"Parsing took {round(response['delta'], 3)}s")

    st.header("Price ($USD)")
    st.write(f"Api call costs {round(response['total_price'],5)}$")

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

@st.cache_data
def tik(words, model="cl100k_base"):
    encoding = tiktoken.get_encoding(model)
    tokens = encoding.encode(words)
    return tokens

def main():
    with st.sidebar:
        API_KEY = st.text_input("Enter your API key")
        if API_KEY:
            if len(API_KEY) > 45 or len(API_KEY) < 40:
                st.warning("Please enter a valid API key")
                API_KEY = None
        if not API_KEY:
            # check if we are in light or dark mode

            theme = st.get_option("theme.primaryColor")

            st.image("static/instructions.png")

            #if theme == "light":
            #    st.image("static/instructions_light.jpg")
            #else:
            #    st.image("static/instructions_dark.jpg")
            

    with tab1:
        st.header("PDF parsing demo")

        if API_KEY:
            info_to_extract = st.text_area("Info to extract", "Policy number, type of Policy, insurance, company, name of policy holder, start/end of Policy and birth date")

            pdf_file = st.file_uploader("Upload a pdf")

            if pdf_file:
                text = ocrPDF(pdf_file)
                autoGPT(text, info_to_extract, API_KEY)
                st.write("To check the ongoing bill, you can click [here](https://api.headswap.com/)")

        else:
            st.warning("Please enter your Headswap-API key in the sidebar to use this tab")

    with tab2:
        st.header("Token & Price calculator")
        model = st.selectbox("Model", ["GPT-3", "GPT-4"])

        prompt = st.text_area("Insert prompt text")

        if prompt:
            char_count = len(prompt)
            num_tokens = tik(prompt)

            GPT3_MAX_TOKEN_COUNT = 16_385
            GPT4_MAX_TOKEN_COUNT = 128_000

            if model == "GPT-3":
                MAX_TOKEN_COUNT = GPT3_MAX_TOKEN_COUNT
            elif model == "GPT-4":
                MAX_TOKEN_COUNT = GPT4_MAX_TOKEN_COUNT
            else:
                st.write("Please select a model")

            information = {
                "Character count": char_count,
                "Number of words": len(prompt.split()),
                "Number of tokens": len(num_tokens),
                "Percentage context length": f"{round(len(num_tokens) / MAX_TOKEN_COUNT * 100, 2)}%"
            }

            st.write(information)

            if len(num_tokens) > MAX_TOKEN_COUNT:
                st.warning(f"Your prompt exceeds the maximum token count of {MAX_TOKEN_COUNT} tokens for the selected model. Please reduce the number of tokens.")

            st.header("Price ($USD)")

            GPT3_PRICE = 0.001 / 1000
            GPT4_PRICE = 0.01 / 1000

            if model == "GPT-3":
                st.write(f"Price: {round(len(num_tokens) * GPT3_PRICE, 4)}$")
            elif model == "GPT-4":
                st.write(f"Price: {round(len(num_tokens) * GPT4_PRICE, 4)}$")
            else:
                st.write("Please select a model")

if __name__ == "__main__":
    main()