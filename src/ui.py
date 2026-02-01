import streamlit as st
import requests
from PIL import Image
import io
import json
import time

# Default to local, but allow override
default_url = "http://127.0.0.1:8000/analyze"

st.set_page_config(
    page_title="Kidney Stone AI Assistant",
    page_icon="🩺",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .report-container {
        border: 2px solid #f0f2f6;
        border-radius: 12px;
        padding: 24px;
        background-color: #ffffff;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .header-style {
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    .metric-box {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        border: 1px solid #e9ecef;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #2c3e50;
    }
    .metric-label {
        font-size: 14px;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .chat-box {
        background-color: #eef2f7;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🩺 MedGemma AI")
st.sidebar.info("v1.5 4B-it (Kaggle Accelerated)")

# URL Configuration
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Connection")
backend_url_root = st.sidebar.text_input("Backend URL", value="http://127.0.0.1:8000").strip()
API_URL = f"{backend_url_root}/analyze"
CHAT_URL = f"{backend_url_root}/chat"

if "ngrok" in API_URL:
    st.sidebar.success("🟢 Connected to Remote GPU")
else:
    st.sidebar.warning("🟠 Local CPU Mode")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📝 Instructions")
st.sidebar.markdown("""
1. Upload CT Slice
2. Automated Analysis
3. Download Report
4. Ask Follow-up Questions
""")

# Main Content
st.title("Kidney Stone Detection & Analysis")
st.markdown("### AI-Powered Radiologist Assistant")

col_upload, col_result = st.columns([1, 1.5])

with col_upload:
    st.subheader("1. Upload Scan")
    uploaded_file = st.file_uploader("Drop DICOM or Image here", type=["dcm", "png", "jpg", "jpeg"])
    
    if uploaded_file:
        try:
            if uploaded_file.name.lower().endswith('.dcm'):
                 st.info("DICOM Uploaded")
            else:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded CT Slice", use_container_width=True)
        except Exception as e:
            st.error("Error loading image")

# Analysis State
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

with col_result:
    st.subheader("2. Clinical Findings")
    
    if uploaded_file and st.button("Run Analysis 🚀", type="primary"):
        with st.spinner("Processing on MedGemma..."):
            try:
                # Prepare File
                uploaded_file.seek(0)
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                
                # API Call
                response = requests.post(API_URL, files=files)
                
                if response.status_code == 200:
                    st.session_state.analysis_result = response.json()
                    st.toast("Analysis Complete!", icon="✅")
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

    # Display Results
    if st.session_state.analysis_result:
        data = st.session_state.analysis_result
        
        # Container styling
        st.markdown('<div class="report-container">', unsafe_allow_html=True)
        
        # Header
        st.markdown(f'<h2 class="header-style">📋 Patient Report: {uploaded_file.name}</h2>', unsafe_allow_html=True)
        
        # Summary Status
        found = data.get("stone_found", False)
        if found:
            st.error("🚨 Kidney Stone DETECTED")
        else:
            st.success("✅ No Kidney Stone Detected")
            
        # Metrics Grid
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Location</div>
                <div class="metric-value">{data.get('location', 'N/A')}</div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Size</div>
                <div class="metric-value">{data.get('size_mm', 'N/A')} mm</div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            urgency = data.get("urgency_level", "Low")
            color = "#dc3545" if urgency == "High" else "#ffc107" if urgency == "Medium" else "#198754"
            st.markdown(f"""
            <div class="metric-box" style="border-bottom: 4px solid {color}">
                <div class="metric-label">Urgency</div>
                <div class="metric-value" style="color: {color}">{urgency}</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("### 📝 Clinical Summary")
        st.info(data.get("patient_summary", "No summary available."))
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Download Button
        report_text = f"""
        MEDICAL REPORT
        --------------------------------
        File: {uploaded_file.name}
        Date: {time.strftime("%Y-%m-%d %H:%M:%S")}
        
        FINDINGS:
        - Stone Detected: {'Yes' if found else 'No'}
        - Location: {data.get('location', 'N/A')}
        - Size: {data.get('size_mm', 'N/A')} mm
        - Urgency: {data.get('urgency_level', 'N/A')}
        
        SUMMARY:
        {data.get('patient_summary', 'N/A')}
        
        Generated by MedGemma 1.5
        --------------------------------
        """
        st.download_button(
            label="💾 Download Report (TXT)",
            data=report_text,
            file_name=f"report_{uploaded_file.name}.txt",
            mime="text/plain"
        )

# Chat Section (Outside the column logic to span full width below)
st.markdown("---")
if st.session_state.analysis_result:
    st.subheader("💬 AI Consultation")
    st.markdown("Ask follow-up questions about this specific scan.")
    
    user_question = st.text_input("Example: 'What treatment is typically recommended for this size?'")
    
    if st.button("Ask MedGemma") and user_question:
        with st.spinner("Consulting..."):
            try:
                uploaded_file.seek(0)
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                payload = {
                    "question": user_question,
                    "context": json.dumps(st.session_state.analysis_result)
                }
                
                chat_response = requests.post(CHAT_URL, files=files, data=payload)
                
                if chat_response.status_code == 200:
                    answer = chat_response.json().get("answer", "No answer received.")
                    st.markdown(f"""
                    <div class="chat-box">
                        <b style='color: #000000;'>Q: {user_question}</b><br><br>
                        <b style='color: #0d6efd;'>🤖 MedGemma:</b> <span style='color: #000000;'>{answer}</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(f"Chat Error: {chat_response.text}")
                    
            except Exception as e:
                st.error(f"Error: {e}")
