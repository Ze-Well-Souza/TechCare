import os
from app import create_app
from pyngrok import ngrok
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Criar a aplicação Flask com a configuração escolhida
config_name = os.environ.get('FLASK_CONFIG') or 'default'
app = create_app(config_name)

# Criar pastas de dados necessárias
os.makedirs(os.path.join(app.config['DIAGNOSTIC_SAVE_PATH']), exist_ok=True)
os.makedirs(os.path.join(app.config['REPAIR_LOGS_PATH']), exist_ok=True)

# Configurar e iniciar Ngrok
def start_ngrok():
    port = 5000
    public_url = ngrok.connect(port).public_url
    print(f' * Ngrok URL externo: {public_url}')
    # Adicionar URL público ao contexto da aplicação
    app.config['BASE_URL'] = public_url
    return public_url

if __name__ == '__main__':
    # Iniciar Ngrok
    ngrok_url = start_ngrok()
    print(f"\n==================================================")
    print(f"🚀 TechCare está em execução!")
    print(f"📱 URL público: {ngrok_url}")
    print(f"🔗 Compartilhe este link com seu amigo para análise")
    print(f"==================================================\n")
    
    # Iniciar a aplicação Flask
    app.run(host='0.0.0.0', port=5000) 