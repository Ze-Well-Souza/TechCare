@echo off
echo ========================================================================
echo Instalando o Ngrok para compartilhamento da aplicacao TechCare
echo ========================================================================
echo.

echo 1. Verificando se o Python esta instalado...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo Python nao encontrado! Por favor, instale o Python 3.8+ e tente novamente.
    pause
    exit /b 1
)

echo.
echo 2. Instalando a biblioteca pyngrok...
pip install pyngrok
if %ERRORLEVEL% NEQ 0 (
    echo Falha ao instalar pyngrok! Verifique sua conexao com a internet.
    pause
    exit /b 1
)

echo.
echo 3. Criando script para executar a aplicacao com ngrok...
(
echo import os
echo from app import create_app
echo from pyngrok import ngrok
echo import logging
echo.
echo # Configuracao de logging
echo logging.basicConfig(
echo     level=logging.INFO,
echo     format='%%^(asctime^)s - %%^(name^)s - %%^(levelname^)s - %%^(message^)s'
echo ^)
echo.
echo # Criar a aplicacao Flask com a configuracao escolhida
echo config_name = os.environ.get^('FLASK_CONFIG'^) or 'default'
echo app = create_app^(config_name^)
echo.
echo # Criar pastas de dados necessarias
echo os.makedirs^(os.path.join^(app.config['DIAGNOSTIC_SAVE_PATH']^), exist_ok=True^)
echo os.makedirs^(os.path.join^(app.config['REPAIR_LOGS_PATH']^), exist_ok=True^)
echo.
echo # Configurar e iniciar Ngrok
echo def start_ngrok^(^):
echo     port = 5000
echo     public_url = ngrok.connect^(port^).public_url
echo     print^(f' * Ngrok URL externo: {public_url}'^)
echo     # Adicionar URL publico ao contexto da aplicacao
echo     app.config['BASE_URL'] = public_url
echo     return public_url
echo.
echo if __name__ == '__main__':
echo     # Iniciar Ngrok
echo     ngrok_url = start_ngrok^(^)
echo     print^(f"\n=================================================="_^)
echo     print^(f"🚀 TechCare esta em execucao!"_^)
echo     print^(f"📱 URL publico: {ngrok_url}"_^)
echo     print^(f"🔗 Compartilhe este link com seu amigo para analise"_^)
echo     print^(f"=================================================="_^)
echo     # Iniciar a aplicacao Flask
echo     app.run^(host='0.0.0.0', port=5000^)
) > run_with_ngrok.py

echo.
echo 4. Instalacao concluida!
echo.
echo ========================================================================
echo Para iniciar a aplicacao com URL publica, execute:
echo   python run_with_ngrok.py
echo ========================================================================
echo.
pause 