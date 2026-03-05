# AI-Elite Interviewer Platform 🚀🎙️

Welcome to the **AI-Elite Interviewer Platform**, an intelligent, multimodal assessment application driven by Artificial Intelligence. Designed to simulate real-world interviews, this platform evaluates candidates on multiple dimensions—audio, visual, and behavioral—to provide a comprehensive performance score and professional portfolio.

## ✨ Key Features

* **Multimodal Analysis Pipeline:** Synchronously captures and processes audio and video streams for unified evaluation.
* **Advanced Vision Tracking:** Leverages **MediaPipe** and **OpenCV** to track eye contact percentage and blink rates, assessing stress stability and engagement in real-time.
* **Intelligent Audio Processing:** Uses **OpenAI's Whisper** model for highly accurate speech-to-text transcription, calculating Words Per Minute (WPM) and pause durations.
* **Deep NLP Engine:** Integrates **HuggingFace (DistilBERT)** to perform sentiment analysis, emotion detection, and track filler word usage.
* **Holistic Scoring System:** Fuses various metrics (Eye Contact, Filler Control, Pacing, Sentiment, Emotional Tone, Stress Stability) to generate an aggregated confidence score.
* **Interactive & Modern UI:** Built with **Streamlit**, featuring a breathtaking modern dark-mode aesthetic with glassmorphism, dynamic Lottie animations, and interactive Plotly charts (Donut Gauges, Radar Charts, Sentiment Timelines).
* **Automated PDF Portfolio:** Generates a downloadable, professional PDF report summarizing the interview metrics and overall performance at the end of the session.

## 🛠️ Technology Stack

* **Frontend / UI:** Streamlit, Streamlit-Lottie, Plotly
* **Computer Vision:** OpenCV, MediaPipe
* **Audio & Machine Learning:** OpenAI Whisper, HuggingFace Transformers (DistilBERT), PyAudio, SciPy
* **Data Processing:** NumPy, Pandas
* **Report Generation:** FPDF, Kaleido

## 📂 Project Structure

```text
AI_Interview_Analyzer/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Project dependencies
├── audio/
│   ├── recorder.py        # Audio capture and recording
│   └── processor.py       # Whisper transcription and audio analytics
├── vision/
│   └── tracker.py         # MediaPipe vision tracking (Eye contact, Blinks)
├── nlp/
│   └── engine.py          # HuggingFace NLP analysis (Sentiment, Emotion, Fillers)
├── scoring/
│   └── fusion.py          # Metric aggregation and confidence scoring logic
├── utils/
│   ├── controller.py      # Session and state management
│   ├── interviewer.py     # Question generation and interviewer module
│   └── report_gen.py      # PDF portfolio generation
└── README.md              # Project documentation
```

## 🚀 Getting Started

### Prerequisites

* Python 3.8+
* A working microphone and webcam

### Installation

1. **Clone the Repository** (or download the source code):
   ```bash
   git clone https://github.com/yourusername/AI_Interview_Analyzer.git
   cd AI_Interview_Analyzer
   ```

2. **Create a Virtual Environment** (Recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On macOS/Linux
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *Note: Depending on your system, you may need to install additional system-level dependencies for PyAudio and OpenCV.*

### Running the Application

Start the Streamlit server:
```bash
streamlit run app.py
```

Navigate to `http://localhost:8501` in your web browser to access the platform.

## 🎮 How to Use

1. **Start the Interview:** Read the current question presented on the dashboard. Click "▶ Ask & Start Recording" to begin. The AI interviewer will ask the question via text-to-speech.
2. **Answer:** Speak clearly into your microphone while looking at your webcam. A real-time video feed and live tracking metrics will be displayed.
3. **Submit:** Click "⏹ Stop & Submit Answer" when you are done. The engines will evaluate your response.
4. **Review Dashboard:** Analyze your holistic competency breakdown, view sentiment timelines, and examine your scores on the interactive charts.
5. **Complete & Export:** Answer all 5 questions to complete the interview. Finally, click "Generate & Download PDF Portfolio" to receive your comprehensive performance report.

## 💡 Future Enhancements

* Integration with Large Language Models (LLMs) (e.g., GPT-4) for robust technical answer evaluation.
* Cloud deployment (AWS/GCP) with scalable asynchronous model inference.
* Customizable interview modes (Behavioral, Technical, Case Study).
* Mock interview history tracking and user authentication.

---
*Built to empower candidates with actionable AI-driven insights.*
