import streamlit as st
import pandas as pd
from utils.db import get_all_sessions, delete_session
from utils.report_gen import generate_report

st.set_page_config(page_title="Candidate History", layout="wide")

st.title("📁 Candidate History")

sessions = get_all_sessions()

if not sessions:
    st.info("No interviews recorded yet. Head over to Setup to start one.")
    st.stop()

# Convert to DataFrame for easy filtering and rendering
df = pd.DataFrame(sessions)

# Sidebar Filters
st.sidebar.header("Filter History")
filter_role = st.sidebar.multiselect("Role", options=df['role'].unique(), default=df['role'].unique())
filter_grade = st.sidebar.multiselect("Grade", options=df['grade'].unique(), default=df['grade'].unique())

filtered_df = df[(df['role'].isin(filter_role)) & (df['grade'].isin(filter_grade))]

st.subheader("Previous Sessions")
st.dataframe(
    filtered_df[['id', 'candidate_name', 'role', 'date', 'score', 'grade']],
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

st.subheader("Actions")
selected_id = st.selectbox("Select Session ID for Action", options=filtered_df['id'].tolist())

c1, c2, c3 = st.columns(3)

if c1.button("View Analytics", use_container_width=True):
    st.session_state.last_session_id = selected_id
    st.switch_page("pages/03_analytics.py")
    
if c2.button("Generate PDF", use_container_width=True):
    try:
        path = generate_report(selected_id)
        with open(path, "rb") as f:
            c2.download_button(
                label="Download Report",
                data=f,
                file_name=f"InterviewIQ_Report_{selected_id}.pdf",
                mime="application/pdf"
            )
        st.success("Report generated!")
    except Exception as e:
        st.error(f"Error generating report: {e}")
        
if c3.button("Delete Session", type="primary", use_container_width=True):
    if delete_session(selected_id):
        st.success(f"Session {selected_id} deleted successfully.")
        st.rerun()
    else:
        st.error("Failed to delete session.")
