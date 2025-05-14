"""
Arquivo WSGI para deploy do TechCare no PythonAnywhere

IMPORTANTE: Este é um EXEMPLO. Você deve editar o arquivo WSGI diretamente na interface do PythonAnywhere.
Ajuste o path abaixo para refletir o caminho real do seu diretório de projeto no PythonAnywhere.
"""

import sys
import os

# Adiciona o diretório do projeto ao path do Python
# SUBSTITUA pelo caminho real do seu projeto no PythonAnywhere
path = '/home/SEU_USUARIO_PYTHONANYWHERE/techcare'
if path not in sys.path:
    sys.path.append(path)

# Definir variáveis de ambiente para produção
os.environ['FLASK_CONFIG'] = 'production'
os.environ['SECRET_KEY'] = 'ef8b22d09137082c194992cc8c3097e0d93422ba83a61a2993ec3169fcee3564'  # Use a chave gerada acima

# Cria pastas de dados necessárias se não existirem
data_path = os.path.join(path, 'data')
diagnostic_path = os.path.join(data_path, 'diagnostics')
repair_path = os.path.join(data_path, 'repair_logs')
diagnostic_storage = os.path.join(data_path, 'diagnostics_storage')

os.makedirs(data_path, exist_ok=True)
os.makedirs(diagnostic_path, exist_ok=True)
os.makedirs(repair_path, exist_ok=True)
os.makedirs(diagnostic_storage, exist_ok=True)

# Importa a aplicação Flask
from wsgi import app as application

