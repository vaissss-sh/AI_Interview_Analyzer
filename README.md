# InterviewIQ — Multimodal AI Interview Analyzer

InterviewIQ is a production-ready Multimodal AI Interview Analyzer. It features real-time transcription, emotion tracking, NLP behavioral parsing, and comprehensive evaluation through a modern Streamlit UI.

## Features
- Real-time Speech-to-Text and NLP Analysis.
- Video and Emotion Tracking using DeepFace & OpenCV.
- Dynamic Question Engine covering multiple roles.
- Detailed scoring radar charts and PDF report generation.

## Setup Instructions

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your API keys:
   ```bash
   cp .env.example .env
   ```
4. Run the application:
   ```bash
   streamlit run app.py
   ```

## Requirements
- Python 3.9+
- See `requirements.txt` for full dependency details.
