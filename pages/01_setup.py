import streamlit as st
import cv2
from utils.controller import start_interview
from utils.interviewer import get_questions_for_role
from vision.tracker import initialize_camera, get_frame, detect_face, release_camera

st.set_page_config(page_title="Interview Setup", layout="wide")

st.title("Interview Setup & Configuration")

# Initialize session state placeholders if not accessed via main app.py
from utils.controller import init_session_state
init_session_state()

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Candidate Details")
    cand_name = st.text_input("Full Name", value="Jane Doe")
    cand_email = st.text_input("Email Address", value="jane.doe@example.com")
    cand_exp = st.selectbox("Experience Level", ["junior", "mid", "senior"])
    
    st.subheader("2. Interview Role")
    role = st.selectbox("Target Role", ["Software Engineer", "Product Manager", "Data Scientist", "HR Manager"])
    
    st.subheader("3. Job Description (Optional)")
    jd_text = st.text_area("Paste JD details here for keyword matching", height=120)

with col2:
    st.subheader("4. Interview Settings")
    q_count = st.radio("Number of Questions", [5, 10, 15], index=0, horizontal=True)
    enable_vision = st.toggle("Enable Video Analysis", value=True)
    enable_coach = st.toggle("Enable Live Coach Tips", value=True)
    
    st.subheader("5. Camera & Media Test")
    if enable_vision:
        if st.button("Test Camera", use_container_width=True):
            placeholder = st.empty()
            try:
                cap = initialize_camera(0)
                # Read just 10 frames to test
                frame_found = False
                for _ in range(10):
                    frame = get_frame(cap)
                    if frame is not None:
                        frame_found = True
                        res = detect_face(frame)
                        if res:
                            x, y, w, h = res["bbox"]
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        # Convert BGR to RGB for stream
                        placeholder.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB", use_container_width=True)
                        break
                release_camera(cap)
                if frame_found:
                    st.success("Camera working correctly.")
                else:
                    st.error("Failed to read frames from camera.")
            except Exception as e:
                st.error(f"Camera Initialization Error: {e}")
    else:
        st.info("Video analysis is disabled. Audio-only mode will be used.")

st.markdown("---")

st.subheader("Ready to Start")
if st.button("🚀 Start Interview", type="primary", use_container_width=True):
    if cand_name and cand_email:
        # Load Questions
        questions = get_questions_for_role(role, cand_exp, q_count)
        
        # Save info
        cand_info = {
            "name": cand_name,
            "email": cand_email,
            "level": cand_exp,
            "jd_text": jd_text,
            "enable_vision": enable_vision,
            "enable_coach": enable_coach
        }
        
        start_interview(cand_info, role, questions)
        st.success("Interview logic initialized! Please navigate to the **Live Interview** page.")
        # Streamlit programmatically switch page (Streamlit > 1.30)
        st.switch_page("pages/02_live_interview.py")
    else:
        st.warning("Please provide candidate name and email.")
