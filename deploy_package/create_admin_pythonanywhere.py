"""
Script para criar usuário administrador no TechCare no ambiente do PythonAnywhere

Este script deve ser executado após a inicialização do banco de dados
para criar um usuário administrador no sistema.
"""
import os
import sys
from pathlib import Path

def create_admin():
    """
    Cria um usuário administrador para o TechCare no PythonAnywhere
    """
    print("=== Criação de Usuário Administrador no TechCare ===")
    
    # Configurar ambiente de produção
    os.environ['FLASK_CONFIG'] = 'production'
    
    # Importar as dependências
    try:
        from app import create_app, db
        from app.models.user import User
        
        # Criando o app
        app = create_app('production')
        
        with app.app_context():
            # Verificar se já existe algum admin
            admin = User.query.filter_by(role='admin').first()
            if admin:
                print(f"Já existe um administrador: {admin.username} ({admin.email})")
                replace = input("Deseja criar outro administrador? (s/n): ")
                if replace.lower() != 's':
                    print("Operação cancelada.")
                    return
            
            # Coletar informações do novo admin
            username = input("Username: ")
            email = input("Email: ")
            name = input("Nome completo: ")
            password = input("Senha: ")
            
            # Criar o usuário
            user = User(
                username=username,
                email=email,
                name=name,
                role='admin',
                active=True
            )
            user.set_password(password)
            
            # Salvar no banco
            db.session.add(user)
            db.session.commit()
            
            print(f"\nUsuário administrador '{username}' criado com sucesso!")
            
    except Exception as e:
        print(f"Erro ao criar administrador: {e}")
        print("Verifique se o banco de dados foi inicializado corretamente.")
    
    print("\n=== Operação concluída! ===")

if __name__ == "__main__":
    create_admin() 