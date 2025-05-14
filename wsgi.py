"""
Ponto de entrada WSGI para o TechCare em produção

Este arquivo serve como ponto de entrada para servidores WSGI como Gunicorn ou uWSGI.
"""

import sys
import os

# Adiciona o diretório da aplicação ao PATH
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

# Importa e cria a aplicação
from app import create_app

# Cria a aplicação usando as configurações de produção
application = create_app('production')

# Para iniciar com Gunicorn:
# gunicorn -w 4 -b 127.0.0.1:8000 wsgi:app

# No PythonAnywhere, 'application' é a variável esperada pelo WSGI
if __name__ == '__main__':
    application.run() 