@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>&1
if not errorlevel 1 (
    py -3.12 --version >nul 2>&1
    if not errorlevel 1 goto use_py
)

python --version 2>&1 | findstr /r /c:"^Python 3\.12\." >nul
if errorlevel 1 (
    echo ERROR: Python 3.12 was not found.
    echo Install Python 3.12, then run this file again.
    exit /b 1
)
set "PYTHON_LAUNCHER=python"
goto create_environment

:use_py
set "PYTHON_LAUNCHER=py -3.12"

:create_environment
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" --version 2>&1 | findstr /r /c:"^Python 3\.12\." >nul
    if errorlevel 1 (
        echo ERROR: The existing .venv does not use Python 3.12.
        echo Remove .venv manually, then run this file again.
        exit /b 1
    )
) else (
    %PYTHON_LAUNCHER% -m venv .venv
    if errorlevel 1 (
        echo ERROR: Could not create the .venv environment.
        exit /b 1
    )
)

echo Installing project dependencies. Internet is needed if packages are not cached.
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
    echo ERROR: Dependency installation failed.
    exit /b 1
)

echo.
echo Installation complete.
echo Start the app with: .venv\Scripts\python.exe -m streamlit run app.py
echo The demo app uses local data; features that call online services need internet.
exit /b 0
