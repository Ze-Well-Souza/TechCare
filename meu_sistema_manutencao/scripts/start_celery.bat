@echo off
REM Script para iniciar o worker do Celery no Windows

REM Definir variáveis de ambiente
set FLASK_ENV=development
set PYTHONPATH=%CD%

REM Ativar ambiente virtual (se estiver usando)
REM call .venv\Scripts\activate

REM Iniciar Celery worker e beat
celery -A app.tasks worker --loglevel=info --beat

REM Manter janela aberta em caso de erro
pause
