import streamlit as st
from deep_translator import GoogleTranslator
from docx import Document
import tempfile
import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import cv2
import numpy as np


def translate_text(text, dest_lang='hi'):
    try:
        if len(text.strip()) == 0:
            return ""
        return GoogleTranslator(source='auto', target=dest_lang).translate(text)
    except:
        return text  # fallback if translation fails

def process_docx_preserve_format(file, lang_code):
    doc = Document(file)
    new_doc = Document()

    for para in doc.paragraphs:
        new_para = new_doc.add_paragraph()
        for run in para.runs:
            original_text = run.text
            translated_text = translate_text(original_text, lang_code)
            new_run = new_para.add_run(translated_text)
            new_run.bold = run.bold
            new_run.italic = run.italic
            new_run.underline = run.underline
            new_run.font.name = run.font.name
            new_run.font.size = run.font.size
        new_para.style = para.style

    output_path = os.path.join(tempfile.gettempdir(), "translated_preserved.docx")
    new_doc.save(output_path)
    return output_path

def process_pdf_translate_opencv(file, lang_code):
    file_bytes = file.read()
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    new_doc = Document()

    for page in doc:
        pix = page.get_pixmap(dpi=300)
        img_bytes = pix.tobytes("png")
        np_img = np.frombuffer(img_bytes, np.uint8)
        cv_img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        text = pytesseract.image_to_string(thresh, lang='eng')

        for line in text.split("\n"):
            if line.strip():
                translated_line = translate_text(line, lang_code)
                new_doc.add_paragraph(translated_line)

    output_path = os.path.join(tempfile.gettempdir(), "translated_pdf_output.docx")
    new_doc.save(output_path)
    return output_path

def process_image_translate_opencv(file, lang_code):
    image = np.asarray(bytearray(file.read()), dtype=np.uint8)
    cv_img = cv2.imdecode(image, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    text = pytesseract.image_to_string(thresh, lang='eng')

    translated = translate_text(text, lang_code)
    new_doc = Document()
    for line in translated.split("\n"):
        new_doc.add_paragraph(line)

    output_path = os.path.join(tempfile.gettempdir(), "translated_image_output.docx")
    new_doc.save(output_path)
    return output_path

# Streamlit UI
st.title("📄 Document/Image Translator with Format Preservation")
uploaded_file = st.file_uploader("Upload a .docx, .pdf, or image file", type=["docx", "pdf", "png", "jpg", "jpeg"])
lang = st.selectbox("Select Output Language", options=[
    ("English", "en"),
    ("Hindi", "hi"),
    ("Marathi", "mr"),
    ("Gujarati", "gu"),
    ("Tamil", "ta"),
    ("Telugu", "te"),
    ("Bengali", "bn"),
    ("French", "fr"),
    ("German", "de"),
    ("Spanish", "es")
], format_func=lambda x: x[0])
lang_code = lang[1]

if uploaded_file:
    st.info(f"Processing file: {uploaded_file.name}")

    if uploaded_file.name.endswith(".docx"):
        output_path = process_docx_preserve_format(uploaded_file, lang_code)
    elif uploaded_file.name.endswith(".pdf"):
        output_path = process_pdf_translate_opencv(uploaded_file, lang_code)
    elif uploaded_file.name.lower().endswith((".png", ".jpg", ".jpeg")):
        output_path = process_image_translate_opencv(uploaded_file, lang_code)
    else:
        st.error("Unsupported file format")
        st.stop()

    st.success("Translation Complete")

    st.download_button("Download Translated DOCX", data=open(output_path, "rb"), file_name="translated_output.docx")
