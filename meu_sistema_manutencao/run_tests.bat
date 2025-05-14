@echo off
call venv\Scripts\activate
python -m pytest tests\ -v --cov=app --cov-report=term-missing
pause
