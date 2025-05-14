"""
Ponto de entrada WSGI para o TechCare em produção

Este arquivo serve como ponto de entrada para servidores WSGI como Gunicorn ou uWSGI.
"""

import os
import sys

# Adiciona o diretório do projeto ao path do Python
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Importa a função de criação da aplicação
from app import create_app

# Cria a aplicação com a configuração de produção
app = create_app('production')

# Para iniciar com Gunicorn:
# gunicorn -w 4 -b 127.0.0.1:8000 wsgi:app

if __name__ == "__main__":
    # Se o arquivo for executado diretamente, inicia a aplicação
    # Útil para testes e ambientes de desenvolvimento, mas para produção use Gunicorn
    app.run() 