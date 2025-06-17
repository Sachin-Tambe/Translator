import streamlit as st
from deep_translator import GoogleTranslator
from docx import Document
import tempfile
import os

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

# Streamlit UI
st.title("📄 DOCX Translator with Full Format Preservation")
uploaded_file = st.file_uploader("Upload a .docx file", type=["docx"])
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
    output_path = process_docx_preserve_format(uploaded_file, lang_code)
    st.success("Translation Complete with Format Preserved")

    with st.expander("View Sample Input and Output"):
        st.subheader("🔹 Original Text Sample:")
        original_doc = Document(uploaded_file)
        original_sample = "\n".join(p.text for p in original_doc.paragraphs[:3] if p.text.strip())
        st.text_area("Original Sample", original_sample, height=150)

        st.subheader("🔸 Translated Text Sample:")
        translated_doc = Document(output_path)
        translated_sample = "\n".join(p.text for p in translated_doc.paragraphs[:3] if p.text.strip())
        st.text_area("Translated Sample", translated_sample, height=150)

    st.download_button("Download Translated DOCX", data=open(output_path, "rb"), file_name="translated_preserved.docx")
