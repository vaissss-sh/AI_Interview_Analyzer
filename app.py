import streamlit as st
import os
from utils.controller import init_session_state
from utils.db import create_tables

# Set page config
st.set_page_config(
    page_title="InterviewIQ - AI Analyzer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    css_path = os.path.join("assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Initialize DB and Session State
create_tables()
init_session_state()

# Hide default Streamlit sidebar nav to implement custom flow, or just let users use it
st.markdown("""
<style>
/* Hide the default page links if you want full control, but multi-page usually handles it nicely */
</style>
""", unsafe_allow_html=True)

st.title("🧠 InterviewIQ")
st.markdown("### Multimodal AI Interview Analyzer")
st.markdown("---")

st.markdown("""
Welcome to **InterviewIQ**. This platform uses state-of-the-art Multimodal AI to track:
- **Audio & Speech**: Tone, pitch, silence ratios, and pacing.
- **Vision & Expression**: Micro-expressions, gaze tracking, posture, and stress detection.
- **NLP & Content**: Vocabulary strength, STAR method usage, JD keyword matching, and sentiment.

👈 **Select a page from the sidebar to begin.**
""")

with st.sidebar:
    st.header("Quick Navigation")
    st.page_link("app.py", label="Home", icon="🏠")
    st.page_link("pages/01_setup.py", label="Setup Interview", icon="⚙️")
    st.page_link("pages/02_live_interview.py", label="Live Interview", icon="🎙️")
    st.page_link("pages/03_analytics.py", label="Analytics Dashboard", icon="📊")
    st.page_link("pages/04_history.py", label="Candidate History", icon="📁")
    
    st.markdown("---")
    st.write("System Status:")
    if "interview_active" in st.session_state and st.session_state.interview_active:
        st.success("🟢 Interview in Progress")
    else:
        st.info("⚪ Idle")
