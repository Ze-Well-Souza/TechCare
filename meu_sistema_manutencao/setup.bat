@echo off
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
pip install pytest pytest-cov flask-testing
echo Ambiente configurado com sucesso!
