import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.db import get_session_by_id, get_all_sessions
from nlp.engine import analyze_answer, get_answer_sentiment_arc, generate_word_cloud_data
from nlp.star_detector import detect_star_components, get_star_feedback

st.set_page_config(page_title="Analytics Dashboard", layout="wide")

st.title("📊 Analytics & Feedback")

# Pick session
session_id_to_load = None
if 'last_session_id' in st.session_state and st.session_state.last_session_id > 0:
    session_id_to_load = st.session_state.last_session_id
else:
    sessions = get_all_sessions()
    if sessions:
        session_id_to_load = sessions[0]['id']
        st.info("Loading most recent session from history.")
    else:
        st.warning("No sessions found. Complete an interview first.")
        st.stop()

session_data = get_session_by_id(session_id_to_load)
if not session_data:
    st.error("Session data not found.")
    st.stop()

bd = session_data.get("breakdown", {})
cand = session_data.get("candidate", {})
metrics = session_data.get("metrics", {})
questions = session_data.get("questions", [])

# ══════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════
tab1, tab2 = st.tabs(["📈 Overview", "😊 Emotion & Voice"])

# ──────────────────────────────────────────────────────────────────────
# TAB 1: OVERVIEW
# ──────────────────────────────────────────────────────────────────────
with tab1:
    # Top metrics row
    m1, m2, m3, m4 = st.columns(4)
    grade = metrics.get('grade', 'N/A')
    overall = metrics.get('overall_score', 0)
    m1.metric("🎯 Overall Score", f"{overall:.1f} / 100")
    m2.metric("📋 Grade", grade)
    m3.metric("👤 Candidate", cand.get('name', 'N/A'))
    m4.metric("💼 Role", cand.get('role', 'N/A'))
    
    st.markdown("---")
    
    col_radar, col_bars = st.columns([1, 1])
    
    # Radar Chart
    with col_radar:
        st.subheader("Competency Radar")
        if bd:
            categories = ['Communication', 'Confidence', 'Technical', 'Emotional IQ', 'Engagement', 'Professionalism']
            values = [bd.get('communication', 0), bd.get('confidence', 0), bd.get('technical', 0),
                      bd.get('emotional_iq', 0), bd.get('engagement', 0), bd.get('professionalism', 0)]
            
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill='toself',
                fillcolor='rgba(108, 99, 255, 0.3)',
                line=dict(color='#6C63FF', width=2),
                marker=dict(size=8)
            ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=10))),
                showlegend=False, height=400,
                margin=dict(l=60, r=60, t=30, b=30)
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        else:
            st.warning("No breakdown data available.")
    
    # Bar Chart of Each Dimension
    with col_bars:
        st.subheader("Score Breakdown")
        if bd:
            df_bar = pd.DataFrame({
                'Dimension': ['Communication', 'Confidence', 'Technical', 'Emotional IQ', 'Engagement', 'Professionalism'],
                'Score': [bd.get('communication', 0), bd.get('confidence', 0), bd.get('technical', 0),
                          bd.get('emotional_iq', 0), bd.get('engagement', 0), bd.get('professionalism', 0)]
            })
            colors = ['#6C63FF' if s >= 70 else '#FFA726' if s >= 50 else '#EF5350' for s in df_bar['Score']]
            fig_bar = px.bar(df_bar, x='Score', y='Dimension', orientation='h',
                             color='Dimension', color_discrete_sequence=colors)
            fig_bar.update_layout(
                xaxis=dict(range=[0, 100]),
                showlegend=False, height=400,
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
# ──────────────────────────────────────────────────────────────────────
# TAB 2: EMOTION & VOICE
# ──────────────────────────────────────────────────────────────────────
with tab2:
    st.subheader("Emotion Timeline")
    
    # Query emotion logs from DB session (stored as list of dicts)
    # For a fresh session, we use session_state data
    emotions = []
    if 'emotions_timeline' in st.session_state and st.session_state.emotions_timeline:
        emotions = st.session_state.emotions_timeline
    
    if emotions:
        df_emo = pd.DataFrame(emotions)
        
        col_line, col_pie = st.columns([2, 1])
        
        with col_line:
            fig_line = px.line(df_emo, x="timestamp", y="confidence", color="emotion",
                               title="Emotion Intensity Over Time",
                               color_discrete_sequence=px.colors.qualitative.Set2)
            fig_line.update_layout(height=400)
            st.plotly_chart(fig_line, use_container_width=True)
        
        with col_pie:
            emo_counts = df_emo['emotion'].value_counts()
            fig_pie = px.pie(values=emo_counts.values, names=emo_counts.index,
                             title="Emotion Distribution",
                             color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No live emotion data was captured in this session. Enable video analysis during setup to track emotions in real-time.")
    
    st.markdown("---")
    st.subheader("Eye Contact & Posture Summary")
    
    ec_col, pos_col, stress_col = st.columns(3)
    eye_pct = cand.get("eye_contact_percent", 70) if cand else 70
    
    with ec_col:
        fig_eye = go.Figure(go.Indicator(
            mode="gauge+number",
            value=eye_pct,
            title={'text': "Eye Contact %"},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': '#4CAF50' if eye_pct > 60 else '#FF9800'},
                   'steps': [{'range': [0, 40], 'color': '#FFEBEE'},
                             {'range': [40, 70], 'color': '#FFF3E0'},
                             {'range': [70, 100], 'color': '#E8F5E9'}]}
        ))
        fig_eye.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_eye, use_container_width=True)
    
    with pos_col:
        posture = cand.get("posture_summary", "upright") if cand else "upright"
        posture_score = {"upright": 90, "leaning": 60, "slouching": 30}.get(posture, 50)
        fig_pos = go.Figure(go.Indicator(
            mode="gauge+number",
            value=posture_score,
            title={'text': f"Posture ({posture.title()})"},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': '#2196F3'},
                   'steps': [{'range': [0, 40], 'color': '#FFEBEE'},
                             {'range': [40, 70], 'color': '#FFF3E0'},
                             {'range': [70, 100], 'color': '#E8F5E9'}]}
        ))
        fig_pos.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_pos, use_container_width=True)
    
    with stress_col:
        stress_count = sum(1 for e in emotions if e.get('emotion') in ['fear', 'angry', 'disgust']) if emotions else 0
        stress_idx = min(100, stress_count * 15)
        fig_stress = go.Figure(go.Indicator(
            mode="gauge+number",
            value=stress_idx,
            title={'text': "Stress Index"},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': '#F44336' if stress_idx > 50 else '#4CAF50'},
                   'steps': [{'range': [0, 30], 'color': '#E8F5E9'},
                             {'range': [30, 60], 'color': '#FFF3E0'},
                             {'range': [60, 100], 'color': '#FFEBEE'}]}
        ))
        fig_stress.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_stress, use_container_width=True)

