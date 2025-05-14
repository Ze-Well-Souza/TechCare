@echo off
echo ========================================================================
echo Iniciando o TechCare com URL publica para compartilhamento...
echo ========================================================================
echo.
echo 1. Iniciando a aplicacao Flask...
start cmd /k "python run.py"
echo.
echo 2. Aguardando a aplicacao iniciar (10 segundos)...
timeout /t 10 /nobreak > nul
echo.
echo 3. Iniciando o Ngrok para criar um tunel seguro...
echo IMPORTANTE: Quando o Ngrok iniciar, copie a URL "Forwarding" 
echo             (ex: https://xxxx-xxx-xx-xx-xx.ngrok-free.app)
echo             e compartilhe com seu amigo para analise.
echo.
echo ========================================================================
ngrok http 5000 