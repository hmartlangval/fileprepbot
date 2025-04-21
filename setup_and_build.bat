@echo off
echo Setting up environment and building MasterApp executable...

REM Set the base_bot version in a single place
set BASE_BOT_VERSION=5.0.0

echo Using base_bot version: %BASE_BOT_VERSION%

REM Check if Python is installed
python --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python and try again.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

REM Install pydantic explicitly (needed for the executable)
pip install pydantic langchain-core langchain_openai

REM Install base_bot if it's not already installed
pip show base_bot > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing base_bot from tar.gz...
    if exist "base_bot-%BASE_BOT_VERSION%.tar.gz" (
        pip install base_bot-%BASE_BOT_VERSION%.tar.gz
    ) else (
        echo base_bot package tar.gz not found!
        echo Please make sure base_bot-%BASE_BOT_VERSION%.tar.gz is in the current directory.
        pause
        exit /b 1
    )
)

REM Extract base_bot package to ensure it's available for the executable
echo Extracting base_bot package for inclusion in the executable...
mkdir temp_extract 2>nul
cd temp_extract
if exist "..\base_bot-%BASE_BOT_VERSION%.tar.gz" (
    tar -xf ..\base_bot-%BASE_BOT_VERSION%.tar.gz
    if exist "base_bot-%BASE_BOT_VERSION%" (
        xcopy /E /I /Y base_bot-%BASE_BOT_VERSION%\base_bot ..\base_bot
    )
) else (
    echo Using installed base_bot package
)
cd ..

REM Build the executable
echo Building executable...
pyinstaller --clean appstart.spec

echo Build completed! The executable is in the dist folder.
pause 