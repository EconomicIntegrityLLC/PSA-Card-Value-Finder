@echo off
echo Starting PSA Card Grading Finder...
echo.
cd /d "%~dp0"
python -m streamlit run app.py
pause
