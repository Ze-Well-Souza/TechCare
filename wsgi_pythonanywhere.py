import sys
import os

# Adiciona o diretório da aplicação ao PATH
# ATENÇÃO: Ajuste este caminho para o diretório correto do seu projeto
path = '/home/Zewell10/TechCare'
if path not in sys.path:
    sys.path.append(path)

# Define variáveis de ambiente
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_CONFIG'] = 'production'

# Verifica se os diretórios de dados existem e os cria se necessário
data_dir = os.path.join(path, 'data')
os.makedirs(data_dir, exist_ok=True)
os.makedirs(os.path.join(data_dir, 'diagnostics'), exist_ok=True)
os.makedirs(os.path.join(data_dir, 'repair_logs'), exist_ok=True)
os.makedirs(os.path.join(data_dir, 'diagnostics_storage'), exist_ok=True)

# Ativa o ambiente virtual, se necessário
activate_this = os.path.join(path, 'venv/bin/activate_this.py')
if os.path.exists(activate_this):
    with open(activate_this) as file_:
        exec(file_.read(), dict(__file__=activate_this))

# Importa e cria a aplicação
from app import create_app

# Cria a aplicação usando as configurações de produção
application = create_app('production') 