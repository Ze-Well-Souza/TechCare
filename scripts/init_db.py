#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para inicializar o banco de dados e criar um usuário administrador padrão
"""

import os
import sys

# Adiciona o diretório pai ao path do sistema para importar os módulos da aplicação
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.user import User
from datetime import datetime

def init_db():
    """
    Inicializa o banco de dados e cria um usuário administrador padrão
    """
    # Cria a aplicação Flask
    app = create_app('development')
    with app.app_context():
        # Cria todas as tabelas
        db.create_all()
        
        # Verifica se já existe algum usuário administrador
        admin = User.query.filter_by(role='admin').first()
        if admin is None:
            # Cria um usuário administrador padrão
            admin = User(
                username='admin',
                email='admin@techcare.com',
                name='Administrador',
                password='admin123',  # Este é um exemplo - altere para uma senha segura em produção!
                role='admin',
                created_at=datetime.utcnow(),
                active=True
            )
            db.session.add(admin)
            
            # Cria um usuário técnico de exemplo
            tech = User(
                username='tecnico',
                email='tecnico@techcare.com',
                name='Técnico de Exemplo',
                password='tecnico123',  # Este é um exemplo - altere para uma senha segura em produção!
                role='tech',
                created_at=datetime.utcnow(),
                active=True
            )
            db.session.add(tech)
            
            # Cria um usuário comum de exemplo
            user = User(
                username='usuario',
                email='usuario@techcare.com',
                name='Usuário de Exemplo',
                password='usuario123',  # Este é um exemplo - altere para uma senha segura em produção!
                role='user',
                created_at=datetime.utcnow(),
                active=True
            )
            db.session.add(user)
            
            # Salva as alterações no banco de dados
            db.session.commit()
            
            print('Usuários iniciais criados com sucesso!')
            print('Administrador: admin / admin123')
            print('Técnico: tecnico / tecnico123')
            print('Usuário: usuario / usuario123')
        else:
            print('Já existe um usuário administrador no banco de dados.')

if __name__ == '__main__':
    init_db() 