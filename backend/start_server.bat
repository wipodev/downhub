@echo off
: venv\Scripts\activate
start uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
