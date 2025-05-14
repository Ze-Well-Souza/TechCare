import os
from app import create_app
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Cria a aplicação Flask com a configuração escolhida
config_name = os.environ.get('FLASK_CONFIG') or 'default'
app = create_app(config_name)

# Cria pastas de dados necessárias
os.makedirs(os.path.join(app.config['DIAGNOSTIC_SAVE_PATH']), exist_ok=True)
os.makedirs(os.path.join(app.config['REPAIR_LOGS_PATH']), exist_ok=True)

if __name__ == '__main__':
    # Indica à Flask que deve exibir mensagens de erro detalhadas
    app.run(debug=True) 