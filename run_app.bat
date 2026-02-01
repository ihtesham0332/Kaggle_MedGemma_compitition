@echo off
@REM Set your Hugging Face Token here or in system environment variables
set HF_TOKEN=hf_YOUR_TOKEN_HERE
echo Starting Kidney Stone Analysis System...

:: Activate Environment
call venv\Scripts\activate

:: Start Backend in Background
echo Starting FastAPI Backend...
start "MedGemma Backend" cmd /k "venv\Scripts\activate && uvicorn src.api:app --reload --port 8000"

:: Wait for backend to initialize
timeout /t 5 >nul

:: Start Frontend
echo Starting Streamlit Frontend...
streamlit run src/ui.py
