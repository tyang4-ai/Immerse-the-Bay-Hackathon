@echo off
REM Quick start script for Flask backend
REM HoloHuman XR - Immerse the Bay 2025

echo ============================================
echo HoloHuman XR Backend Server
echo Immerse the Bay 2025 Hackathon
echo ============================================
echo.

REM Check if we're in Backend directory
if not exist "ecg_api.py" (
    echo ERROR: ecg_api.py not found!
    echo Please run this script from the Backend directory.
    echo Current directory: %CD%
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo WARNING: Virtual environment not found at venv\Scripts\python.exe
    echo Attempting to use system Python...
    echo.
    set PYTHON_CMD=python
) else (
    echo Using virtual environment: venv\Scripts\python.exe
    echo.
    set PYTHON_CMD=venv\Scripts\python.exe
)

REM Display network info
echo Network Information:
echo -------------------
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set IP=%%a
    set IP=!IP:~1!
    echo Local IP: !IP!
)
echo Localhost: 127.0.0.1
echo Default Port: 5000
echo.

echo For Unity Editor (PC): Use http://localhost:5000
echo For Quest 2 VR: Use http://YOUR_PC_IP:5000
echo.

REM Check if model file exists
if not exist "model\model.hdf5" (
    echo WARNING: Model file not found at model\model.hdf5
    echo Backend will run in simulation mode.
    echo.
)

REM Check if API key is set (optional)
if "%ANTHROPIC_API_KEY%"=="" (
    echo INFO: ANTHROPIC_API_KEY not set - Using fallback mode
    echo This is NORMAL and EXPECTED for the hackathon demo!
    echo.
)

echo Starting Flask server...
echo Press Ctrl+C to stop the server
echo ============================================
echo.

%PYTHON_CMD% ecg_api.py

if %errorlevel% neq 0 (
    echo.
    echo ============================================
    echo ERROR: Server failed to start!
    echo ============================================
    echo.
    echo Possible fixes:
    echo 1. Install dependencies: pip install -r requirements.txt
    echo 2. Check if port 5000 is already in use
    echo 3. Verify Python is installed
    echo.
    pause
)
