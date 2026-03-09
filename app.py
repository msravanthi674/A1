import streamlit as st
import os
from dotenv import load_dotenv
from engine import get_engine

load_dotenv()

st.set_page_config(page_title="Autonomous CEO Researcher", page_icon="🕵️", layout="wide")

# Premium CSS for "AI Aurora" Theme
st.markdown("""
<style>
    /* Luminous Radial Background */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #1e1b4b 0%, #0f172a 50%, #020617 100%);
        color: #cbd5e1;
    }
    
    /* Glassmorphism Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.9) !important;
        backdrop-filter: blur(25px);
        border-right: 1px solid rgba(139, 92, 246, 0.3);
    }
    
    /* Log Box (Process Terminal) */
    .log-box {
        background-color: #010409;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid transparent;
        background-image: linear-gradient(#010409, #010409), 
                          linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        background-origin: border-box;
        background-clip: padding-box, border-box;
        color: #a78bfa;
        height: 300px;
        overflow-y: auto;
        font-family: 'Fira Code', monospace;
        font-size: 0.85rem;
    }
    
    /* Report Card */
    .report-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        padding: 2.5rem;
        border-radius: 16px;
        border: 1px solid rgba(139, 92, 246, 0.2);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        color: #e2e8f0;
    }

    h1, h2, h3 {
        background: linear-gradient(135deg, #60a5fa 30%, #c084fc 70%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }

    /* Button Styling */
    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(168, 85, 247, 0.4);
    }
</style>
""", unsafe_allow_html=True)

st.title("🕵️ Autonomous Founder/CEO Researcher")
st.markdown("Assignment 1: Internet exploration agent that browses and gathers deep context.")

with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Groq API Key", value=os.getenv("GROQ_API_KEY", ""), type="password")
    if not api_key:
        st.warning("Please enter your Groq API Key to proceed.")

col1, col2 = st.columns([1, 1])

with col1:
    target_name = st.text_input("Who should I research?", placeholder="e.g. Jensen Huang, Sam Altman...")
    search_btn = st.button("🚀 Start Autonomous Research", use_container_width=True)

with col2:
    st.markdown("### 🛠️ Process Logs")
    log_placeholder = st.empty()
    log_placeholder.markdown('<div class="log-box">> Ready for input...</div>', unsafe_allow_html=True)

if search_btn and api_key:
    app = get_engine(api_key)
    initial_state = {
        "target": target_name,
        "search_queries": [],
        "raw_info": [],
        "structured_data": {},
        "logs": [],
        "iteration": 0
    }
    
    logs = []
    
    with st.status(f"Exploring data for {target_name}...", expanded=True) as status:
        for output in app.stream(initial_state):
            for key, value in output.items():
                if "logs" in value:
                    for l in value["logs"]:
                        logs.append(f"> {l}")
                        log_placeholder.markdown(f'<div class="log-box">{"<br>".join(logs)}</div>', unsafe_allow_html=True)
                
                if "structured_data" in value:
                    report_content = value["structured_data"].get("report", "")

        status.update(label="Research Complete!", state="complete")
    
    st.markdown("---")
    st.markdown("### 📋 Final Research Report")
    st.markdown(f'<div class="report-card">{report_content}</div>', unsafe_allow_html=True)
elif search_btn and not api_key:
    st.error("API Key missing!")
