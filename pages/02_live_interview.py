import streamlit as st
import io
import os
import tempfile
import time
import cv2
import numpy as np
from datetime import datetime
from utils.controller import get_current_question, next_question, end_interview

st.set_page_config(page_title="Live Interview", layout="wide")

if 'interview_active' not in st.session_state or not st.session_state.interview_active:
    st.warning("No active interview. Please go to Setup and start a new session.")
    st.stop()

cand_info = st.session_state.candidate_info

# Import audio recorder
from audio_recorder_streamlit import audio_recorder

# Import speech recognition
import speech_recognition as sr

# Import vision modules (fault-tolerant)
from vision.emotion_detector import analyze_frame, DEEPFACE_AVAILABLE
from vision.gaze_estimator import estimate_gaze
from vision.tracker import detect_face, detect_posture

st.title("🎙️ Live Interview Session")

# ── Question Display ──────────────────────────────────────────────────
q_idx = st.session_state.current_q_index
total_q = len(st.session_state.questions)

st.info(f"**Question {q_idx + 1} of {total_q}:**\n\n### {get_current_question()}")

# ── Time Elapsed ──────────────────────────────────────────────────────
elapsed = int((datetime.utcnow() - st.session_state.start_time).total_seconds())
mins, secs = divmod(elapsed, 60)

col_time, col_progress = st.columns([1, 3])
col_time.metric("⏱️ Time Elapsed", f"{mins:02d}:{secs:02d}")
col_progress.progress((q_idx + 1) / total_q, text=f"Progress: {q_idx + 1}/{total_q} questions")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# TWO-COLUMN LAYOUT: Left = Video + Emotion | Right = Audio + Transcript
# ══════════════════════════════════════════════════════════════════════
col_video, col_audio = st.columns([1, 1.2])

# ── LEFT: Webcam Emotion & Behavior Analysis ──────────────────────────
with col_video:
    st.subheader("📹 Behavior Analysis")
    
    enable_vision = cand_info.get("enable_vision", False)
    
    if enable_vision:
        st.caption("Capturing a snapshot for emotion, eye contact, and posture analysis.")
        
        # Use Streamlit's camera_input for webcam capture
        camera_image = st.camera_input("Take a snapshot for analysis", key=f"cam_{q_idx}_{elapsed // 10}")
        
        if camera_image is not None:
            # Convert to OpenCV format
            file_bytes = np.asarray(bytearray(camera_image.read()), dtype=np.uint8)
            frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            
            if frame is not None:
                # ── Face Detection ──
                face_data = detect_face(frame)
                
                emotion_result = {"emotion": "neutral", "confidence": 0}
                gaze_direction = "unknown"
                posture_status = "unknown"
                
                if face_data:
                    # ── Emotion Analysis ──
                    emotion_result = analyze_frame(frame)
                    
                    # ── Gaze / Eye Contact ──
                    gaze_direction = estimate_gaze(frame, face_data["landmarks"])
                    
                    # ── Posture ──
                    posture_status = detect_posture(frame)
                    
                    # Store in session state for scoring later
                    st.session_state.emotions_timeline.append({
                        "timestamp": elapsed,
                        "emotion": emotion_result["emotion"],
                        "confidence": emotion_result["confidence"]
                    })
                    
                    # Track eye contact
                    if 'gaze_log' not in st.session_state:
                        st.session_state.gaze_log = []
                    st.session_state.gaze_log.append(gaze_direction)
                    
                    # Calculate eye contact percentage
                    direct_count = sum(1 for g in st.session_state.gaze_log if g == "direct")
                    total_gaze = len(st.session_state.gaze_log)
                    eye_contact_pct = round((direct_count / max(1, total_gaze)) * 100, 1)
                    
                    # Store for scoring
                    st.session_state.candidate_info["eye_contact_percent"] = eye_contact_pct
                    st.session_state.candidate_info["posture_summary"] = posture_status
                
                # Display Results
                r1, r2 = st.columns(2)
                
                emo_label = emotion_result["emotion"]
                emo_conf = emotion_result["confidence"]
                emo_color = {"happy": "🟢", "neutral": "🔵", "sad": "🟡", "angry": "🔴", "fear": "🟠", "surprise": "🟣", "disgust": "🔴"}.get(emo_label, "⚪")
                
                r1.metric(f"{emo_color} Emotion", f"{emo_label.title()}", f"{emo_conf:.0f}% confidence")
                
                gaze_icon = "👁️" if gaze_direction == "direct" else "👀"
                r2.metric(f"{gaze_icon} Eye Contact", gaze_direction.title())
                
                r3, r4 = st.columns(2)
                posture_icon = "🧍" if posture_status == "upright" else "😔"
                r3.metric(f"{posture_icon} Posture", posture_status.title())
                
                if 'gaze_log' in st.session_state and st.session_state.gaze_log:
                    direct_count = sum(1 for g in st.session_state.gaze_log if g == "direct")
                    eye_pct = round((direct_count / len(st.session_state.gaze_log)) * 100, 1)
                    r4.metric("👁️ Eye Contact %", f"{eye_pct}%")
                
                # Stress warning
                if emo_label in ["fear", "angry"] and emo_conf > 50:
                    st.error("⚠️ Elevated stress detected. Take a deep breath and compose yourself.")
        else:
            st.caption("📷 Click 'Take a snapshot' above to capture and analyze your expression.")
    else:
        st.info("📷 Video analysis is disabled. Enable it in Setup to track emotions, eye contact, and posture.")
        
        # Show emotion timeline count if any data exists
        if st.session_state.emotions_timeline:
            st.metric("Emotion Snapshots Captured", len(st.session_state.emotions_timeline))

# ── RIGHT: Speech-to-Text Answer ──────────────────────────────────────
with col_audio:
    st.subheader("🎤 Record Your Answer")
    st.caption("Click the mic to record. Click again to stop. Speech is auto-transcribed.")
    
    # Audio recorder widget
    audio_bytes = audio_recorder(
        text="Click to record",
        recording_color="#e74c3c",
        neutral_color="#6c757d",
        icon_size="2x",
        pause_threshold=3.0,
        key=f"audio_recorder_{q_idx}"
    )
    
    # Process the recorded audio
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        
        with st.spinner("🔄 Transcribing..."):
            try:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                    tmp_file.write(audio_bytes)
                    tmp_path = tmp_file.name
                
                recognizer = sr.Recognizer()
                with sr.AudioFile(tmp_path) as source:
                    audio_data = recognizer.record(source)
                
                transcript = recognizer.recognize_google(audio_data)
                os.unlink(tmp_path)
                
                # Append transcript
                existing = st.session_state.questions[q_idx].get("answer_transcript", "")
                updated = f"{existing} {transcript}".strip() if existing else transcript
                st.session_state.questions[q_idx]["answer_transcript"] = updated
                
                st.success("✅ Transcribed!")
                
            except sr.UnknownValueError:
                st.warning("⚠️ Could not understand audio. Try speaking more clearly.")
            except sr.RequestError as e:
                st.error(f"❌ Service error: {e}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
                if 'tmp_path' in locals():
                    try: os.unlink(tmp_path)
                    except: pass
    
    # Show current transcript
    st.markdown("---")
    st.subheader("📝 Transcript")
    current_transcript = st.session_state.questions[q_idx].get("answer_transcript", "")
    
    if current_transcript:
        st.text_area("Answer", value=current_transcript, height=180, disabled=True,
                     key=f"transcript_display_{q_idx}", label_visibility="collapsed")
        if st.button("🗑️ Clear & Re-record", key=f"clear_{q_idx}"):
            st.session_state.questions[q_idx]["answer_transcript"] = ""
            st.rerun()
    else:
        st.caption("_No answer recorded yet._")

st.markdown("---")

# ── Controls ──────────────────────────────────────────────────────────
st.subheader("Controls")
c1, c2 = st.columns(2)

if c1.button("➡️ Next Question", use_container_width=True, disabled=(q_idx >= total_q - 1)):
    next_question()
    st.rerun()

if c2.button("🛑 End Interview", type="primary", use_container_width=True):
    end_interview()
    st.switch_page("pages/03_analytics.py")

# ── Coach Tips (optional) ─────────────────────────────────────────────
if cand_info.get("enable_coach", False):
    st.markdown("---")
    st.subheader("💡 Coach Tips")
    st.info("Use the **STAR method** (Situation, Task, Action, Result) for behavioral questions.")
    
    # Dynamic tips based on captured data
    if st.session_state.emotions_timeline:
        last_emo = st.session_state.emotions_timeline[-1]
        if last_emo["emotion"] in ["fear", "angry"]:
            st.warning("You seem stressed. Take a moment to breathe before answering.")
        elif last_emo["emotion"] == "happy":
            st.success("Great energy! Your positive expression will make a strong impression.")
