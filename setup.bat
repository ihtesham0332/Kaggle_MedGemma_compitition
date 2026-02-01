@echo off
setlocal

echo ==========================================
echo Setting up Kidney Stone Analysis Environment
echo ==========================================

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.10+.
    exit /b 1
)

:: Create Virtual Environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Virtual environment "venv" already exists.
)

:: Activate Virtual Environment
call venv\Scripts\activate

:: Install Dependencies
echo Installing dependencies...
pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org

if %errorlevel% neq 0 (
    echo Failed to install dependencies.
    exit /b 1
)

echo.
echo ==========================================
echo Environment Setup Complete!
echo ==========================================
