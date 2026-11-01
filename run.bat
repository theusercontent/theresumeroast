@echo off
setlocal
cd /d "%~dp0"

echo.
echo ========================================
echo    The Workbench - Windows launcher
echo ========================================
echo.

if not exist "app.py" (
    echo ERROR: app.py was not found. Please extract the entire app before running this file.
    goto :error
)

if not exist ".venv\Scripts\python.exe" (
    echo Setting up a Python virtual environment...
    py -3 --version >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON_CMD=py -3"
    ) else (
        python --version >nul 2>&1
        if errorlevel 1 (
            echo ERROR: Python was not found. Install Python 3.10 or newer from https://www.python.org/downloads/
            echo During installation, select "Add Python to PATH", then run this file again.
            goto :error
        )
        set "PYTHON_CMD=python"
    )
    call :create_venv
    if errorlevel 1 goto :error
)

echo Installing or checking dependencies. This may take a few minutes the first time...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Dependency installation failed. Check your internet connection and try again.
    goto :error
)

echo.
echo Starting The Workbench. Your browser should open automatically.
echo If it does not, open the Local URL shown below in your browser.
echo Keep this window open while using the app. Press Ctrl+C to stop it.
echo.
".venv\Scripts\python.exe" -m streamlit run app.py
if errorlevel 1 (
    echo ERROR: The app stopped unexpectedly.
    goto :error
)
exit /b 0

:create_venv
%PYTHON_CMD% -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)"
if errorlevel 1 (
    echo ERROR: Python 3.10 or newer is required. Please install a newer version of Python.
    exit /b 1
)
%PYTHON_CMD% -m venv .venv
if errorlevel 1 (
    echo ERROR: Could not create the virtual environment. Check your Python installation.
    exit /b 1
)
exit /b 0

:error
echo.
pause
exit /b 1
