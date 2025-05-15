"""
Configuração para os testes do TechCare

Este arquivo define fixtures e configurações utilizadas pelos testes.
"""

import pytest
import sys
import os
import sqlalchemy as sa
from unittest.mock import patch

# Adicionando o diretório raiz ao sys.path para permitir importações corretas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importações corretas agora
from app import create_app, db
from app.models.user import User
from app.models.role import Role, PermissionType

@pytest.fixture
def app():
    """Cria e configura uma instância do app Flask para testes."""
    # Configura o SQLAlchemy para permitir declarações de tabela duplicadas
    # Verifica se kwargs já contém extend_existing para evitar duplicação
    old_new = sa.Table.__new__
    
    def _patched_table_new(cls, *args, **kwargs):
        if 'extend_existing' not in kwargs:
            kwargs['extend_existing'] = True
        if 'sqlite_autoincrement' not in kwargs:
            kwargs['sqlite_autoincrement'] = True
        return old_new(cls, *args, **kwargs)
    
    sa.Table.__new__ = _patched_table_new
    
    # Cria uma nova instância da aplicação com configuração de teste
    app = create_app('testing')
    
    with app.app_context():
        # Garante que o user_loader esteja registrado corretamente
        @app.login_manager.user_loader
        def load_user(user_id):
            return db.session.get(User, int(user_id))
        
        # Limpa o banco de dados e cria todas as tabelas
        db.drop_all()
        db.create_all()
        
        yield app
        
        # Limpeza após os testes
        db.session.remove()
        db.drop_all()
    
    # Restaura o comportamento original
    sa.Table.__new__ = old_new

@pytest.fixture
def client(app):
    """Um cliente de teste para a aplicação."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Um runner de teste para comandos CLI."""
    return app.test_cli_runner()

@pytest.fixture
def test_user(app):
    """Cria um usuário de teste no banco de dados."""
    with app.app_context():
        # Verificar se já existe o Role ou criar um novo
        user_role = db.session.query(Role).filter_by(name='User').first()
        if not user_role:
            user_role = Role(name='User', description='Usuário comum')
            user_role.add_permission(PermissionType.VIEW_DASHBOARD)
            user_role.add_permission(PermissionType.RUN_DIAGNOSTICS)
            db.session.add(user_role)
            db.session.commit()
        
        user = User(
            username='testuser',
            email='test@example.com',
            role=user_role,
            active=True
        )
        user.password = 'password123'  # Usando a propriedade password em vez de set_password
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def test_admin(app):
    """Cria um usuário administrador de teste no banco de dados."""
    with app.app_context():
        # Verificar se já existe o Role ou criar um novo
        admin_role = db.session.query(Role).filter_by(name='Admin Master').first()
        if not admin_role:
            admin_role = Role(name='Admin Master', description='Administrador com acesso total')
            admin_role.add_permission(PermissionType.ADMIN_ACCESS)
            admin_role.add_permission(PermissionType.MANAGE_USERS)
            admin_role.add_permission(PermissionType.VIEW_DASHBOARD)
            admin_role.add_permission(PermissionType.RUN_DIAGNOSTICS)
            admin_role.add_permission(PermissionType.RUN_REPAIRS)
            admin_role.add_permission(PermissionType.VIEW_LOGS)
            db.session.add(admin_role)
            db.session.commit()
        
        admin = User(
            username='testadmin',
            email='admin@example.com',
            role=admin_role,
            active=True
        )
        admin.password = 'adminpass123'  # Usando a propriedade password em vez de set_password
        db.session.add(admin)
        db.session.commit()
        return admin

@pytest.fixture
def test_technician(app):
    """Cria um usuário técnico de teste no banco de dados."""
    with app.app_context():
        # Verificar se já existe o Role ou criar um novo
        tech_role = db.session.query(Role).filter_by(name='Technician').first()
        if not tech_role:
            tech_role = Role(name='Technician', description='Técnico com permissões especiais')
            tech_role.add_permission(PermissionType.RUN_DIAGNOSTICS)
            tech_role.add_permission(PermissionType.RUN_REPAIRS)
            tech_role.add_permission(PermissionType.VIEW_DASHBOARD)
            db.session.add(tech_role)
            db.session.commit()
        
        tech = User(
            username='testtechnician',
            email='tech@example.com',
            role=tech_role,
            active=True
        )
        tech.password = 'techpass123'  # Usando a propriedade password em vez de set_password
        db.session.add(tech)
        db.session.commit()
        return tech

@pytest.fixture
def auth_client(app, client, test_user):
    """Um cliente com login já realizado."""
    with app.app_context():
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        return client

class AuthActions:
    """Classe auxiliar para ações de autenticação nos testes."""
    
    def __init__(self, client):
        self._client = client
        
    def login(self, username='testuser', password='password123'):
        """Faz login com o usuário fornecido."""
        return self._client.post(
            '/login',
            data={'username': username, 'password': password},
            follow_redirects=True
        )
        
    def logout(self):
        """Faz logout do usuário."""
        return self._client.get('/logout', follow_redirects=True)

@pytest.fixture
def auth(client):
    """Fixture para realizar ações de autenticação nos testes."""
    return AuthActions(client)

@pytest.fixture
def admin_client(app, client, test_admin):
    """Um cliente com login de administrador já realizado."""
    with app.app_context():
        client.post('/auth/login', data={
            'username': 'testadmin',
            'password': 'adminpass123'
        }, follow_redirects=True)
        return client

# Fixtures para mock de recursos do sistema
@pytest.fixture
def mock_disk_usage():
    """Mock para psutil.disk_usage"""
    with patch('psutil.disk_usage') as mock:
        mock.return_value = type('obj', (object,), {
            'total': 100 * 1024 * 1024 * 1024,  # 100 GB
            'used': 50 * 1024 * 1024 * 1024,    # 50 GB
            'free': 50 * 1024 * 1024 * 1024,    # 50 GB
            'percent': 50.0                     # 50%
        })
        yield mock

@pytest.fixture
def mock_cpu_percent():
    """Mock para psutil.cpu_percent"""
    with patch('psutil.cpu_percent') as mock:
        mock.return_value = 30.0  # 30% de uso de CPU
        yield mock

@pytest.fixture
def mock_virtual_memory():
    """Mock para psutil.virtual_memory"""
    with patch('psutil.virtual_memory') as mock:
        mock.return_value = type('obj', (object,), {
            'total': 8 * 1024 * 1024 * 1024,  # 8 GB
            'available': 4 * 1024 * 1024 * 1024,  # 4 GB
            'used': 4 * 1024 * 1024 * 1024,  # 4 GB
            'percent': 50.0  # 50% de uso
        })
        yield mock 