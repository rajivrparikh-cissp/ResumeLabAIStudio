@echo off
title Resume Lab AI Studio - Local Private Launch
echo ==============================================================================
echo             RESUME LAB AI STUDIO - 100%% PRIVATE LOCAL LAUNCHER
echo ==============================================================================
echo Zero-Cloud PII Architecture: All resumes, credentials, and data remain strictly
echo on your local machine.
echo ==============================================================================

cd /d "%~dp0"

:: 1. Check Python installation
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python 3.10+ is required but not found in PATH.
    echo Please install Python from https://www.python.org/downloads/
    echo (Make sure to check "Add Python to PATH" during installation)
    pause
    exit /b 1
)

:: 2. Check / Create Virtual Environment
if not exist ".venv" (
    echo [*] Creating virtual environment (.venv)...
    python -m venv .venv
)

:: 3. Install / Verify Dependencies
echo [*] Verifying dependencies...
.venv\Scripts\python.exe -m pip install -q --disable-pip-version-check -r requirements.txt

:: 4. Check Ollama (Optional Local LLM)
where ollama >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [*] Detected Ollama on your system.
) else (
    echo [i] Ollama not detected. (You can also bring your own Gemini/OpenAI API key in the UI)
)

:: 5. Launch Studio Web App
echo [*] Launching Resume Lab Studio on http://localhost:5050 ...
start "" "http://localhost:5050"
.venv\Scripts\python.exe app\server.py

pause
