import pymupdf4llm
import streamlit as st
import tempfile
import os

def process_pdf(uploaded_file):
    """
    Converts a PDF file to Markdown using pymupdf4llm.
    Returns: markdown text (str) and page count (int)
    """
    try:
        # Create a temporary file because pymupdf4llm needs a file path
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        # Extract Markdown (The Magic Step)
        # This keeps bolding, headers, and lists intact!
        md_text = pymupdf4llm.to_markdown(tmp_path)
        
        # Cleanup
        os.remove(tmp_path)
        
        # Basic Stats
        word_count = len(md_text.split())
        est_minutes = round(word_count / 150)  # Avg reading speed
        
        return {
            "text": md_text,
            "word_count": word_count,
            "est_reading_time": est_minutes
        }
        
    except Exception as e:
        st.error(f"Error parsing PDF: {e}")
        return None