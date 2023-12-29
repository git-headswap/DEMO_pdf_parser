from openai import OpenAI
import streamlit as st
from pdf2image import convert_from_bytes
import pytesseract
import requests
import json
import tiktoken
import xmltodict

st.set_page_config(page_title="Headswap Demo", page_icon="static/logo.png", layout="wide")

tab1, tab2, tab3, tab4 = st.tabs(["PDF Parsing", "Token Calculator", "RAM - XLMParsing", "AutoGPT - email"])

@st.cache_data
def autoGPT(message, info_to_extract, API_KEY, model="gpt-3.5-turbo-1106"):
    payload = {
        "model": model,
        "prompt": f"You will receive an ocr PDF, your job is to extract the following information: {info_to_extract} as JSON. If the information is not provided please write N/A.",
        "text": f"Here is the pdf ocr: {message}",
        "max_tokens": 2048,
        "temperature": 0,
    }

    headers = {
        "api_key_2": API_KEY,
        "peek": "true"
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
    st.write(f"That is {round(1/response['total_price'])} docs/$")

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

def sidebar():
    with st.sidebar:
        API_KEY = st.text_input("Enter your API key")
        if API_KEY:
            if len(API_KEY) > 45 or len(API_KEY) < 40:
                st.warning("Please enter a valid API key")
                API_KEY = None
        else:
            st.image("static/instructions.png")
    return API_KEY

def pdfParsingDemo(API_KEY):
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

def tokenCalculator():
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

def xlmParsingDemo():
    @st.cache_data
    def xmltodict_parse(xml_data):
        return xmltodict.parse(xml_data)
    def parse_dict(dict_data):
        # Get developer information
        data = dict_data["developer"]
        name = data["name"]
        data_id = data["id"]

        # Get developers programs
        programs = data["programs"]["program"]
        n_programs = len(programs)
        st.write(f"Found {n_programs} programs from {name} with id {data_id}")
        
        # Get properties from programs
        program_to_watch = st.slider("Select program to inspect", 0, n_programs-1, 0)
        example_program = programs[program_to_watch]
        program_name = example_program["name"]
        program_id = example_program["id"]
        program_properties = example_program["properties"]["property"]

        # if property is a dict:
        if isinstance(program_properties, dict):
            n_program_properties = 1
            program_properties = [program_properties]
        else:
            n_program_properties = len(program_properties)

        st.write(f"Looking at program {program_name} with name {program_id} and {n_program_properties} properties")

        try:
            images = example_program["images"]["image"]
            if images:
                st.image(images)
        except:
            st.error("Could not get the image")

        show_program = st.checkbox("Show sample program", value=False, key="show_program")
        if show_program:
            st.write(example_program)

        show_property = st.checkbox("Show sample property", value=False, key="show_property")
        if show_property:
            st.write(program_properties[0])

    st.header("XLM parsing demo")
    # dropdown
    upload_type = st.selectbox("Upload type", ["Text", "File"])
    if upload_type == "File":
        file = st.file_uploader("Upload XML File", type=['xml'])
        if file:
            xml_data = file.read()
            try:
                data_dict = xmltodict_parse(xml_data)
                st.success("File Uploaded Successfully")
            except:
                st.error("Invalid XML File")
            parse_dict(data_dict)
    elif upload_type == "Text":
        xml_data = st.text_area("Paste XML data here")
        if xml_data:
            try:
                data_dict = xmltodict_parse(xml_data)
                st.success("File Uploaded Successfully")
            except:
                st.error("Invalid XML File")
            parse_dict(data_dict)

def emailGPT(API_KEY):
    st.header("AutoGPT - email")
    #st.write("This is a demo of the new AutoGPT input service. The service is currently in beta. To use the service tell Davide to add your email to the beta and forward an email to autoagentshs@gmail.com.")
    if API_KEY:
        if st.button("Refresh Emails"):
            headers = {
                "api_key_2": API_KEY
            }
            r = requests.get("https://api.headswap.com/refresh", headers=headers)
            try:
                r_json = json.loads(r.text)
            except:
                r_json = r.text
            st.write(r_json)
    else:
        st.warning("Please enter your Headswap-API key in the sidebar to use this tab")

def main():
    API_KEY = sidebar()
    with tab1:
        pdfParsingDemo(API_KEY)
    with tab2:
        tokenCalculator()
    with tab3:
        xlmParsingDemo()
    with tab4:
        emailGPT(API_KEY)
        

if __name__ == "__main__":
    main()