@echo off
echo ==========================================
echo Hugging Face Authentication
echo ==========================================
echo You need to log in to access the MedGemma model.
echo Please copy your Access Token from: https://huggingface.co/settings/tokens
echo.

:: Activate Environment
call venv\Scripts\activate

:: Check if huggingface_hub is installed (it should be if setup ran, but let's be safe)
pip install huggingface_hub >nul 2>&1

:: Run Login
huggingface-cli login

echo.
echo Authentication Complete!
pause
