import streamlit as st
import time
import cv2
import queue
import numpy as np
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests

# Set page config FIRST
st.set_page_config(
    page_title="AI-Elite Interviewer Platform",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for Modern Midnight & Glassmorphism
st.markdown("""
<style>
    /* Global Background and text color */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    
    /* Headers */
    h1, h2, h3, h4 {
        color: #f8fafc;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 300;
        letter-spacing: 0.5px;
    }
    
    h1 {
        background: -webkit-linear-gradient(45deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }

    /* Glassmorphism Cards */
    div[data-testid="stVerticalBlock"] > div.css-1r6slb0, 
    div[data-testid="stVerticalBlock"] > div.css-12oz5g7,
    div.stExpander {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }

    /* Primary Buttons */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #3b82f6 0%, #6366f1 100%);
        color: white;
        border-radius: 12px;
        border: none;
        padding: 12px 28px;
        font-size: 16px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
    }
    
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.6);
    }
    
    div.stButton > button:first-child:active {
        transform: translateY(1px);
    }

    /* Metric Values */
    div[data-testid="stMetricValue"] {
        color: #38bdf8;
        font-weight: 600;
    }
    div[data-testid="stMetricDelta"] {
        color: #34d399;
    }
    
    /* Hide top padding */
    .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

from utils.controller import SessionController
from audio.recorder import AudioRecorder
from audio.processor import AudioTranscriber
from vision.tracker import VideoTracker
from nlp.engine import NLPAnalyzer
from scoring.fusion import calculate_score
from utils.interviewer import Interviewer
from utils.report_gen import ReportGenerator

# --- HELPER FUNCTIONS ---

def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

@st.cache_resource
def load_models():
    """Cache models so they are only loaded once per app session."""
    with st.spinner("Initializing AI-Elite Models (Whisper & DistilBERT)..."):
        transcriber = AudioTranscriber("base")
        analyzer = NLPAnalyzer()
    return transcriber, analyzer

def save_plotly_static(fig, filepath):
    try:
        # Requires kaleido
        fig.write_image(filepath)
    except Exception as e:
        print(f"Failed to generate static plotly image: {e}")

def get_radar_chart(aggregated_res):
    if not aggregated_res:
        return go.Figure()
        
    # Calculate Averages across completed questions
    avg_eye = sum([r['eye_contact'] for r in aggregated_res]) / len(aggregated_res)
    avg_fillers = sum([r['breakdown']['filler_score'] for r in aggregated_res]) / len(aggregated_res)
    avg_wpm = sum([r['breakdown']['wpm_score'] for r in aggregated_res]) / len(aggregated_res)
    avg_sentiment = sum([r['breakdown']['sentiment_score'] for r in aggregated_res]) / len(aggregated_res)
    avg_emotion = sum([r['breakdown']['emotion_score'] for r in aggregated_res]) / len(aggregated_res)
    avg_stability = sum([r['breakdown']['blink_score'] for r in aggregated_res]) / len(aggregated_res)
    
    categories = ['Eye Contact', 'Filler Control', 'Pacing (WPM)', 'Sentiment', 'Emotional Tone', 'Stress Stability']
    values = [avg_eye, avg_fillers, avg_wpm, avg_sentiment, avg_emotion, avg_stability]
    
    fig = go.Figure(data=[
        go.Bar(
            x=categories, 
            y=values,
            marker_color=['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'],
            text=[f"{v:.0f}" for v in values],
            textposition='auto',
        )
    ])

    fig.update_layout(
        title="Holistic Competency Overview",
        title_font=dict(color="white", size=18),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#f8fafc", size=12),
        yaxis=dict(range=[0, 100], showgrid=True, gridcolor="rgba(255,255,255,0.1)", color="rgba(255,255,255,0.8)"),
        xaxis=dict(showgrid=False, color="rgba(255,255,255,0.8)"),
        margin=dict(t=50, b=40, l=40, r=40),
        showlegend=False
    )
    return fig

def get_donut_gauge(value, title, color):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'color': "white", 'size': 18}},
        number = {'font': {'color': color}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': color, 'line': {'color': "white", 'width': 1}},
            'bgcolor': "rgba(0,0,0,0.1)",
            'borderwidth': 2,
            'bordercolor': "rgba(255,255,255,0.2)",
            'steps': [
                {'range': [0, 50], 'color': "rgba(239, 68, 68, 0.3)"},
                {'range': [50, 80], 'color': "rgba(245, 158, 11, 0.3)"},
                {'range': [80, 100], 'color': "rgba(16, 185, 129, 0.3)"}
            ],
        }
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), height=250, margin=dict(t=30, b=20, l=20, r=20))
    return fig

def get_sentiment_line(aggregated_res):
    if not aggregated_res:
         return go.Figure()
         
    x_vals = [f"Q{i+1}" for i in range(len(aggregated_res))]
    y_vals = [r['breakdown']['sentiment_score'] for r in aggregated_res]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_vals, y=y_vals, 
        mode='lines+markers',
        line=dict(color='#818cf8', width=3, shape='spline'),
        marker=dict(size=10, color='#38bdf8', line=dict(color='white', width=2))
    ))
    
    fig.update_layout(
        title="Sentiment Timeline",
        title_font=dict(color="white", size=18),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white"),
        xaxis=dict(showgrid=False, color="rgba(255,255,255,0.5)"),
        yaxis=dict(range=[0, 105], showgrid=True, gridcolor="rgba(255,255,255,0.1)", color="rgba(255,255,255,0.5)"),
        margin=dict(t=40, b=30, l=40, r=20)
    )
    return fig

# --- INITIALIZATION ---
transcriber, analyzer = load_models()
controller = SessionController()
interviewer = Interviewer()

if 'current_q_index' not in st.session_state:
    st.session_state.current_q_index = 0
if 'aggregated_results' not in st.session_state:
    st.session_state.aggregated_results = []
if 'interview_complete' not in st.session_state:
    st.session_state.interview_complete = False

lottie_recording = load_lottieurl("https://lottie.host/9e00041f-72f5-4f40-9a2c-f6eb05ccf106/UOS2X5A2e8.json") # generic mic pulse
lottie_done = load_lottieurl("https://lottie.host/50e26b1c-3b99-4c8d-8cd6-c67d609c1bed/C7KkG43c3f.json") # generic check

# --- MAIN APP UI ---

st.title("AI-Elite Interviewer Platform")
st.markdown("*" + "An intelligent, multimodal assessment using MediaPipe, Streamlit, and HuggingFace." + "*")

# --- TOP STATS HEADER ---
header_col1, header_col2, header_col3 = st.columns([1, 1, 1])

with header_col1:
    st.write(f"### Question {min(st.session_state.current_q_index + 1, 5)} / 5")
    
# Layout: Left side for interactions, Right side for real-time reporting
main_col1, main_col2 = st.columns([4, 6])

with main_col1:
    st.markdown("### Interview Console")
    console_container = st.container()
    
    with console_container:
        # 1. State: Complete
        if st.session_state.interview_complete:
            st.success("Interview Successfully Completed.")
            if lottie_done:
                st_lottie(lottie_done, height=150, key="done")
            
            # Export Report Button
            if st.button("Generate & Download PDF Portfolio"):
                with st.spinner("Compiling Professional Portfolio..."):
                    # Save static charts first
                    radar_fig = get_radar_chart(st.session_state.aggregated_results)
                    save_plotly_static(radar_fig, "temp_radar_chart.png")
                    
                    sent_fig = get_sentiment_line(st.session_state.aggregated_results)
                    save_plotly_static(sent_fig, "temp_sentiment_chart.png")
                    
                    # Calculate overall averages
                    total_qs = len(st.session_state.aggregated_results)
                    avg_final = sum([r['score'] for r in st.session_state.aggregated_results]) / total_qs
                    avg_wpm = sum([r['wpm'] for r in st.session_state.aggregated_results]) / total_qs
                    total_fillers = sum([r['fillers_count'] for r in st.session_state.aggregated_results])
                    avg_eye = sum([r['eye_contact'] for r in st.session_state.aggregated_results]) / total_qs
                    
                    overall_metrics = {
                        "final_score": avg_final,
                        "avg_wpm": avg_wpm,
                        "total_fillers": total_fillers,
                        "avg_eye_contact": avg_eye,
                        "avg_emotion": st.session_state.aggregated_results[-1]['emotion'] # simplistic approximation
                    }
                    
                    rg = ReportGenerator()
                    pdf_path = rg.generate(st.session_state.aggregated_results, overall_metrics)
                    
                    with open(pdf_path, "rb") as pdf_file:
                        st.download_button(label="📥 Download Portfolio",
                                           data=pdf_file,
                                           file_name="Interview_Performance_Portfolio.pdf",
                                           mime="application/pdf")
            
        # 2. State: In Progress Options
        else:
            q_text = interviewer.get_question(st.session_state.current_q_index)
            st.info(f"**Current Question:**\n{q_text}")
            
            # Start button
            if not controller.state.is_recording and not controller.state.is_processing and not controller.state.is_speaking:
                if st.button("▶ Ask & Start Recording", use_container_width=True):
                    # Ask Question via Speech (This blocks until finished)
                    interviewer.ask_question(st.session_state.current_q_index, controller)
                    
                    # START RECORDING AUTOMATICALLY
                    controller.start_recording()
                    st.session_state.start_time = time.time()
                    
                    try:
                        # Thread 1: Vision
                        vision_thread = VideoTracker(controller)
                        vision_thread.start()
                        
                        # Thread 2: Audio
                        audio_filename = f"temp_q_{st.session_state.current_q_index}.wav"
                        st.session_state.current_audio_file = audio_filename
                        audio_thread = AudioRecorder(controller, output_filename=audio_filename)
                        audio_thread.start()
                        
                        st.session_state.vision_thread = vision_thread
                        st.session_state.audio_thread = audio_thread
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to start hardware: {e}")
                        controller.stop_recording()
            
            # During Recording UI
            if controller.state.is_speaking:
                st.warning("Interviewer is speaking... 🔊")
                
            elif controller.state.is_recording:
                st.warning("Recording Answer... 🔴")
                if lottie_recording:
                    st_lottie(lottie_recording, height=100)
                    
                if st.button("⏹ Stop & Submit Answer", type="primary", use_container_width=True):
                    controller.stop_recording()
                    
                    if 'vision_thread' in st.session_state:
                         st.session_state.vision_thread.join()
                    if 'audio_thread' in st.session_state:
                         st.session_state.audio_thread.join()
                         
                    duration = (time.time() - st.session_state.start_time) / 60.0
                    controller.update_state(duration=duration)
                    st.rerun()
                    
                # Real-time Video UI display
                video_placeholder = st.empty()
                metric_placeholder = st.empty()
                while controller.state.is_recording:
                     if not controller.vision_queue.empty():
                         try:
                             frame_bytes = controller.vision_queue.get_nowait()
                             image = cv2.imdecode(np.frombuffer(frame_bytes, np.uint8), cv2.IMREAD_COLOR)
                             image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                             video_placeholder.image(image, channels="RGB", use_container_width=True)
                         except queue.Empty:
                             pass
                     state = controller.get_state()
                     metric_placeholder.markdown(f"**Tracking** | Eye Contact: `{state['eye_contact_percentage']:.0f}%` | Blinks: `{state['blink_count']}`")
                     time.sleep(0.05)
            
            # Post-Recording Processing
            if controller.state.is_processing and not controller.state.is_recording:
                 st.info("⚙️ Evaluating Response... (Analyzing Audio & Vision)")
                 
                 # 1. Pipeline: Audio/Whisper
                 audio_res = transcriber.transcribe(st.session_state.current_audio_file)
                 # 2. Pipeline: NLP
                 nlp_res = analyzer.analyze(audio_res['transcript'])
                 
                 state = controller.get_state()
                 duration_minutes = getattr(controller.state, 'duration', 0.1)
                 
                 metrics = {
                     "wpm": audio_res['wpm'],
                     "transcript_length": len(audio_res['words']),
                     "fillers_count": nlp_res['fillers_count'],
                     "sentiment_score": nlp_res['sentiment_score'],
                     "emotion": nlp_res['emotion'],
                     "pauses_seconds": audio_res['pauses_seconds'],
                     "eye_contact_percentage": state['eye_contact_percentage'],
                     "blink_count": state['blink_count'],
                     "duration_minutes": duration_minutes if duration_minutes > 0 else 0.1
                 }
                 
                 score_result = calculate_score(metrics)
                 
                 controller.update_state(is_processing=False, transcript=audio_res['transcript'])
                 
                 # Store Aggregated Data
                 st.session_state.aggregated_results.append({
                     "question": q_text,
                     "transcript": audio_res['transcript'],
                     "score": score_result['final_score'],
                     "wpm": audio_res['wpm'],
                     "fillers_count": nlp_res['fillers_count'],
                     "emotion": nlp_res['emotion'],
                     "eye_contact": state['eye_contact_percentage'],
                     "breakdown": score_result['breakdown']
                 })
                 
                 # Increment Sequence
                 st.session_state.current_q_index += 1
                 if st.session_state.current_q_index >= 5:
                     st.session_state.interview_complete = True
                     
                 st.rerun()


# --- RIGHT SIDE: ANALYTICS DASHBOARD ---
with main_col2:
    st.markdown("### Interactive Diagnostics")
    
    if len(st.session_state.aggregated_results) == 0:
        st.info("Awaiting first response to generate competency charts... 📊")
    else:
        # Calculate dynamic final score from aggregations
        current_avg_score = sum([r['score'] for r in st.session_state.aggregated_results]) / len(st.session_state.aggregated_results)
        current_avg_eye = sum([r['eye_contact'] for r in st.session_state.aggregated_results]) / len(st.session_state.aggregated_results)
        
        # Row 1: Gauges
        g_col1, g_col2 = st.columns(2)
        with g_col1:
            st.plotly_chart(get_donut_gauge(current_avg_score, "Confidence Score", "#3b82f6"), use_container_width=True)
        with g_col2:
             st.plotly_chart(get_donut_gauge(current_avg_eye, "Eye Contact %", "#10b981"), use_container_width=True)
             
        # Row 2: Radar Chart
        st.markdown("#### Holistic Competency Breakdown")
        radar_fig = get_radar_chart(st.session_state.aggregated_results)
        st.plotly_chart(radar_fig, use_container_width=True)
        
        # Row 3: Sentiment
        sent_fig = get_sentiment_line(st.session_state.aggregated_results)
        st.plotly_chart(sent_fig, use_container_width=True)
        
        # Transcript Expander
        with st.expander("Review Past Transcripts"):
             for i, res in enumerate(st.session_state.aggregated_results):
                 st.markdown(f"**Q{i+1}: {res['question']}**")
                 st.caption(f"*Response:* {res['transcript']}")
                 st.caption(f"Score: `{res['score']}` | Emotion: `{res['emotion']}`")
                 st.divider()
