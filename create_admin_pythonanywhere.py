#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para criar um usuário administrador no TechCare após o deploy no PythonAnywhere

Este script deve ser executado no ambiente do PythonAnywhere após o deploy
para criar um usuário administrador inicial no sistema.
"""

import os
import sys
import getpass
import re
from datetime import datetime

# Tenta importar o Flask e o app
try:
    from app import create_app, db
    from app.models.user import User, Role
except ImportError:
    print("Erro ao importar módulos necessários.")
    print("Certifique-se de que está no diretório correto e que o ambiente virtual está ativado.")
    print("Execute: source venv/bin/activate")
    sys.exit(1)

def validate_email(email):
    """Valida o formato de um endereço de e-mail"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Valida a força da senha"""
    if len(password) < 8:
        return False, "A senha deve ter pelo menos 8 caracteres."
    
    if not any(c.isupper() for c in password):
        return False, "A senha deve conter pelo menos uma letra maiúscula."
    
    if not any(c.islower() for c in password):
        return False, "A senha deve conter pelo menos uma letra minúscula."
    
    if not any(c.isdigit() for c in password):
        return False, "A senha deve conter pelo menos um número."
    
    return True, "Senha válida"

def create_admin_user():
    """Cria um usuário administrador no sistema"""
    print("\n=== Criação de Usuário Administrador para o TechCare ===\n")
    
    # Inicializa o aplicativo Flask em modo de produção
    app = create_app('production')
    
    # Usa o contexto do aplicativo
    with app.app_context():
        # Verifica se já existem usuários administradores
        admin_role = Role.query.filter_by(name='admin').first()
        if admin_role:
            existing_admins = User.query.filter_by(role_id=admin_role.id).all()
            if existing_admins:
                print(f"Já existem {len(existing_admins)} usuários administradores no sistema:")
                for admin in existing_admins:
                    print(f"  - {admin.username} ({admin.email})")
                
                if input("\nDeseja criar um novo admin mesmo assim? (s/N): ").lower() != 's':
                    print("Operação cancelada.")
                    return
        
        # Coleta informações do novo administrador
        print("\nPor favor, forneça as informações para o novo administrador:")
        
        # Username
        while True:
            username = input("Username: ").strip()
            if len(username) >= 3:
                # Verifica se o username já existe
                if User.query.filter_by(username=username).first():
                    print("Este username já está em uso. Escolha outro.")
                else:
                    break
            else:
                print("O username deve ter pelo menos 3 caracteres.")
        
        # Email
        while True:
            email = input("Email: ").strip()
            if validate_email(email):
                # Verifica se o email já existe
                if User.query.filter_by(email=email).first():
                    print("Este email já está em uso. Escolha outro.")
                else:
                    break
            else:
                print("Email inválido. Forneça um endereço de email válido.")
        
        # Nome completo
        name = input("Nome completo: ").strip()
        
        # Senha
        while True:
            password = getpass.getpass("Senha: ")
            valid, message = validate_password(password)
            if valid:
                # Confirma a senha
                confirm_password = getpass.getpass("Confirme a senha: ")
                if password == confirm_password:
                    break
                else:
                    print("As senhas não coincidem.")
            else:
                print(message)
        
        # Verifica se o papel de administrador existe ou cria um novo
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            print("Papel de administrador não encontrado. Criando...")
            admin_role = Role(name='admin', description='Administrador do sistema')
            db.session.add(admin_role)
            try:
                db.session.commit()
                print("Papel de administrador criado com sucesso.")
            except Exception as e:
                db.session.rollback()
                print(f"Erro ao criar papel de administrador: {str(e)}")
                return
        
        # Cria o usuário administrador
        try:
            admin_user = User(
                username=username,
                email=email,
                name=name,
                active=True,
                role_id=admin_role.id,
                created_at=datetime.now()
            )
            admin_user.set_password(password)
            db.session.add(admin_user)
            db.session.commit()
            
            print("\n✅ Usuário administrador criado com sucesso!")
            print(f"Username: {username}")
            print(f"Email: {email}")
            print(f"Nome: {name}")
            print("\nVocê pode fazer login no sistema com essas credenciais.")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Erro ao criar usuário administrador: {str(e)}")

if __name__ == "__main__":
    create_admin_user() 