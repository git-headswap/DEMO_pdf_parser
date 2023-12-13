# Streamlit OpenAI App for OCR and Information Extraction

## Overview
This Streamlit web app uses OpenAI's GPT models to extract specific information from OCR-processed PDF files. It allows users to upload PDFs, choose a model, and extract required information.

## Imports
- `openai`: For accessing OpenAI GPT models.
- `streamlit as st`: For building the web app interface.
- `pdf2image`: For converting PDF files into images.
- `pytesseract`: For performing Optical Character Recognition (OCR) on images.

## API Key Input
- Users can enter their OpenAI API key through a sidebar input.

## Model Selection
- Provides a sidebar option for users to select from various GPT models.

## Model Pricing
- A dictionary `model_price` containing the cost per token for different GPT models.

## Functions

### parsePDF
- **Purpose**: To send a request to the GPT model for extracting specified information from OCR text.
- **Parameters**: 
  - `message`: The OCR text from a PDF.
  - `model`: The chosen GPT model.
  - `info_to_extract`: Information to extract from the text.
- **Functionality**: 
  - Sends a request to OpenAI.
  - Displays extracted information.
  - Estimates the cost based on token usage.

### ocrPDF
- **Purpose**: To convert a PDF file to images and perform OCR.
- **Parameters**:
  - `pdf_file`: The uploaded PDF file.
- **Functionality**: 
  - Converts PDF to images.
  - Performs OCR on each page to extract text.

## PDF Parsing Demo
- This section of the app allows users to:
  - Enter information they want to extract.
  - Upload a PDF file.
  - View the extracted information and estimated cost using `ocrPDF` and `parsePDF` functions.