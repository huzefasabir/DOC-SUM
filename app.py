import os
import time
import logging
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from file_processing import process_file
from gemini_utils import (
    configure_gemini,
    extract_summary,
    split_into_paragraphs,
    generate_questions
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Setup Gemini API key
gemini_api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("MODEL", "gemini-1.5-flash")  # Get model from env or use default
if not gemini_api_key:
    logger.warning("GEMINI_API_KEY not found in .env file")

# Initialize session state
if 'generated_questions' not in st.session_state:
    st.session_state.generated_questions = []
if 'paragraph_index' not in st.session_state:
    st.session_state.paragraph_index = 0
if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "upload"
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = ""
if 'paragraphs' not in st.session_state:
    st.session_state.paragraphs = []
if 'summary' not in st.session_state:
    st.session_state.summary = ""
if 'api_error' not in st.session_state:
    st.session_state.api_error = None

# Helper Functions
def summarize_text(text):
    """Summarize the extracted text using Gemini."""
    st.session_state.api_error = None
    
    try:
      
        status, model_instance = configure_gemini(gemini_api_key, model)
        if not status:
            logger.error(f"Failed to configure Gemini API: {model_instance}")
            st.session_state.api_error = "Gemini API configuration failed. Please check your API key."
            return None
            
        # Extract summary
        summary = extract_summary(text, model_instance)
        return summary
    except Exception as e:
        logger.error(f"Error in summarize_text: {str(e)}")
        st.session_state.api_error = f"Error generating summary: {str(e)}"
        return None

def process_paragraphs(text):
    """Split the text into paragraphs."""
    st.session_state.api_error = None
    
    try:
        status, model_instance = configure_gemini(gemini_api_key, model)
        if not status:
            logger.error(f"Failed to configure Gemini API: {model_instance}")
            st.session_state.api_error = "Gemini API configuration failed. Please check your API key."
            return []
            
        # Split into paragraphs
        paragraphs = split_into_paragraphs(text, model_instance)
        return paragraphs
    except Exception as e:
        logger.error(f"Error in process_paragraphs: {str(e)}")
        st.session_state.api_error = f"Error processing paragraphs: {str(e)}"
        return []

def create_questions(paragraph):
    """Create questions and answers from the paragraph."""
    st.session_state.api_error = None
    
    try:
        # Configure Gemini with API key
        status, model_instance = configure_gemini(gemini_api_key, model)
        if not status:
            logger.error(f"Failed to configure Gemini API: {model_instance}")
            st.session_state.api_error = "Gemini API configuration failed. Please check your API key."
            return []
            
        # Generate questions
        questions = generate_questions(paragraph, model_instance)
        return questions
    except Exception as e:
        logger.error(f"Error in create_questions: {str(e)}")
        st.session_state.api_error = f"Error generating questions: {str(e)}"
        return []

def next_paragraph():
    """Move to the next paragraph."""
    st.session_state.paragraph_index += 1
    st.session_state.show_answer = False
    st.session_state.generated_questions = []

def previous_paragraph():
    """Move to the previous paragraph."""
    st.session_state.paragraph_index -= 1
    st.session_state.show_answer = False
    st.session_state.generated_questions = []

def toggle_answer():
    """Toggle showing the answer."""
    st.session_state.show_answer = not st.session_state.show_answer

def switch_tab(tab_name):
    """Switch to a different tab."""
    st.session_state.active_tab = tab_name

# UI
st.title("DOC-SUM")

# Main navigation buttons
col1, col2, col3 = st.columns(3)
if col1.button("📄 Upload Content"):
    switch_tab("upload")
if col2.button("📝 Review Summary"):
    switch_tab("summary")
if col3.button("❓ Practice Questions"):
    switch_tab("practice")

# Upload Tab
if st.session_state.active_tab == "upload":
    st.header("Upload Your Study Material")
    
    uploaded_file = st.file_uploader("Choose a PDF file or image", type=["pdf", "png", "jpg", "jpeg"])
    
    col1, col2 = st.columns(2)
    process_button = col1.button("Process File")
    clear_button = col2.button("Clear")
    
    if process_button and uploaded_file is not None:
        with st.spinner("Processing file..."):
            # Extract text from file
            text = process_file(uploaded_file)
            if text:
                st.session_state.extracted_text = text
                
                # Generate summary
                with st.spinner("Generating summary..."):
                    summary = summarize_text(text)
                    if summary:
                        st.session_state.summary = summary
                    
                # Split into paragraphs
                with st.spinner("Processing paragraphs..."):
                    paragraphs = process_paragraphs(text)
                    if paragraphs:
                        st.session_state.paragraphs = paragraphs
                        st.session_state.paragraph_index = 0
                
                # Switch to summary tab
                switch_tab("summary")
            else:
                logger.error("Failed to extract text from the uploaded file.")
    
    if clear_button:
        st.session_state.extracted_text = ""
        st.session_state.summary = ""
        st.session_state.paragraphs = []
        st.session_state.generated_questions = []
        st.session_state.paragraph_index = 0
        st.session_state.show_answer = False
        st.session_state.api_error = None

# Summary Tab
elif st.session_state.active_tab == "summary":
    st.header("Document Summary")
    
    if st.session_state.summary:
        st.markdown(st.session_state.summary)
        
        if st.button("Continue to Practice Questions"):
            switch_tab("practice")
    else:
        st.info("No summary available. Please upload and process a file first.")
        if st.button("Go to Upload"):
            switch_tab("upload")

# Practice Questions Tab
elif st.session_state.active_tab == "practice":
    st.header("Practice Questions")
    
    if not st.session_state.paragraphs:
        st.info("No content to generate questions from. Please upload and process a file first.")
        if st.button("Go to Upload"):
            switch_tab("upload")
    else:
        # Display paragraph navigation
        total_paragraphs = len(st.session_state.paragraphs)
        st.markdown(f"**Paragraph {st.session_state.paragraph_index + 1} of {total_paragraphs}**")
        
        # Display current paragraph
        current_paragraph = st.session_state.paragraphs[st.session_state.paragraph_index]
        st.markdown("### Content")
        st.write(current_paragraph)
        
        # Generate questions button
        if st.button("Generate Questions for this Paragraph"):
            with st.spinner("Generating questions..."):
                questions = create_questions(current_paragraph)
                if questions:
                    st.session_state.generated_questions = questions
                    st.experimental_rerun()
        
        # Display questions
        if st.session_state.generated_questions:
            st.markdown("### Questions")
            for i, qa_pair in enumerate(st.session_state.generated_questions):
                st.markdown(f"**Q{i+1}: {qa_pair['question']}**")
                
                if st.session_state.show_answer:
                    st.markdown(f"**A{i+1}:** {qa_pair['answer']}")
            
            # Show/Hide answer button
            if st.button("Show/Hide Answers"):
                toggle_answer()
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        if st.session_state.paragraph_index > 0:
            if col1.button("Previous Paragraph"):
                previous_paragraph()
        
        if st.session_state.paragraph_index < total_paragraphs - 1:
            if col2.button("Next Paragraph"):
                next_paragraph() 
