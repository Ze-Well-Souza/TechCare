# Script para adicionar um usuário de teste ao banco de dados
import sys
import os

# Adiciona o diretório do projeto ao sys.path para permitir importações relativas
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app import create_app, db
from app.models.user import User  # Supondo que o modelo User está em app.models.user
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Verifica se o usuário já existe
    test_user = User.query.filter_by(username='manusteste').first()
    if not test_user:
        # Cria um novo usuário de teste
        new_user = User(
            username='manusteste',
            email='manus.teste@manus.ai',
            name='Manus Teste User'  # Corrigido de full_name para name
        )
        new_user.password = 'manus123'  # Usando o setter para definir a senha e gerar o hash
        db.session.add(new_user)
        db.session.commit()
        print(f"Usuário 'manusteste' criado com sucesso.")
    else:
        print(f"Usuário 'manusteste' já existe.")

