import unittest
from app import create_app
from app.models.user import User
from app.models.role import Role, PermissionType
from app.extensions import db
from flask_login import login_user, current_user
import json

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        """Configurar ambiente de teste"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        
        with self.app.app_context():
            # Limpar banco de dados
            db.drop_all()
            db.create_all()
            
            # Criar roles de teste
            admin_role = Role(
                name='Admin Master', 
                permissions=[
                    PermissionType.USER_MANAGEMENT, 
                    PermissionType.SYSTEM_CONFIG
                ]
            )
            viewer_role = Role(
                name='Visualizador', 
                permissions=[PermissionType.DASHBOARD_READ]
            )
            db.session.add(admin_role)
            db.session.add(viewer_role)
            
            # Criar usuários de teste
            admin_user = User(
                username='admin_test', 
                email='admin@test.com', 
                password='senhaforte123',
                role=admin_role
            )
            viewer_user = User(
                username='viewer_test', 
                email='viewer@test.com', 
                password='senhaforte123',
                role=viewer_role
            )
            db.session.add(admin_user)
            db.session.add(viewer_user)
            
            db.session.commit()
    
    def test_login_success(self):
        """Testar login bem-sucedido"""
        response = self.client.post('/auth/login', json={
            'username': 'admin_test',
            'password': 'senhaforte123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json)
    
    def test_login_failure(self):
        """Testar login com credenciais inválidas"""
        response = self.client.post('/auth/login', json={
            'username': 'admin_test',
            'password': 'senhaerrada'
        })
        self.assertEqual(response.status_code, 401)
    
    def test_role_based_access_control(self):
        """Testar controle de acesso baseado em roles"""
        # Login como visualizador
        login_response = self.client.post('/auth/login', json={
            'username': 'viewer_test',
            'password': 'senhaforte123'
        })
        token = login_response.json['access_token']
        
        # Tentar acessar endpoint de gerenciamento de usuários
        response = self.client.get('/users', headers={
            'Authorization': f'Bearer {token}'
        })
        self.assertEqual(response.status_code, 403)
    
    def test_permission_check(self):
        """Testar verificação de permissões"""
        # Login como admin
        login_response = self.client.post('/auth/login', json={
            'username': 'admin_test',
            'password': 'senhaforte123'
        })
        token = login_response.json['access_token']
        
        # Acessar endpoint de gerenciamento de usuários
        response = self.client.post('/users', json={
            'username': 'novo_usuario',
            'email': 'novo@teste.com',
            'password': 'senhaforte123'
        }, headers={
            'Authorization': f'Bearer {token}'
        })
        self.assertEqual(response.status_code, 201)

if __name__ == '__main__':
    unittest.main()
