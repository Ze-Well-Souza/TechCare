import os
import sys

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.tasks import celery_app

def main():
    """
    Script para iniciar o worker do Celery
    """
    # Configurar variáveis de ambiente
    os.environ.setdefault('FLASK_ENV', 'development')
    
    # Iniciar worker do Celery
    argv = [
        'worker', 
        '--loglevel=info', 
        '--beat'  # Inclui o agendador de tarefas
    ]
    
    celery_app.start(argv)

if __name__ == '__main__':
    main()
