@echo off
echo Verificando ambiente Python...
where python
if %errorlevel% neq 0 (
    echo Python não encontrado no PATH
    exit /b 1
)

python --version

echo Criando ambiente virtual...
python -m venv venv
call venv\Scripts\activate

echo Instalando dependências...
pip install -r requirements.txt
pip install pytest pytest-cov flask-testing

echo Executando testes...
python -m pytest tests\ -v --cov=app --cov-report=term-missing

pause
