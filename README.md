# Study Notes Q&A Generator

This Streamlit application helps students generate questions and answers from their study materials. Upload PDF documents or images, and the app will:

1. Extract text from the documents
2. Generate a summary using Google Gemini API
3. Split the text into meaningful paragraphs
4. Create practice questions and answers from selected paragraphs

## Setup

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key (required)

### Installation

1. Clone the repository
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with your Gemini API key:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   MODEL=gemini-pro
   ```

## Running the Application

Start the Streamlit app:
```
streamlit run app.py
```
The app will be available at http://localhost:8501

## Files

- `app.py`: Streamlit application with integrated Gemini API calls
- `file_processing.py`: Handles PDF and image text extraction
- `gemini_utils.py`: Utility functions for interacting with the Gemini API
- `.env`: Contains your Gemini API key (not included in repository)

## Features

- PDF document processing
- Image OCR using Tesseract
- Text summarization using Google Gemini AI
- Paragraph extraction
- Question and answer generation
- Interactive UI for practicing with generated questions
- Model selection (gemini-pro or gemini-pro-vision)

## Dependencies

- Streamlit: Web UI
- Google Generative AI API: AI processing
- PyPDF2: PDF processing
- Tesseract OCR: Image text extraction
- Pillow: Image handling 