import unittest
from app import create_app
from app.models.user import User
from app.models.role import Role
from app.extensions import db
import json

class UserManagementTestCase(unittest.TestCase):
    def setUp(self):
        """Configurar ambiente de teste"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        
        with self.app.app_context():
            # Limpar banco de dados
            db.drop_all()
            db.create_all()
            
            # Criar role de admin
            admin_role = Role(
                name='Admin Master', 
                permissions=['USER_MANAGEMENT']
            )
            db.session.add(admin_role)
            
            # Criar usuário admin para testes
            admin_user = User(
                username='admin_test', 
                email='admin@test.com', 
                password='senhaforte123',
                role=admin_role
            )
            db.session.add(admin_user)
            db.session.commit()
    
    def _login_admin(self):
        """Realizar login como admin"""
        response = self.client.post('/auth/login', json={
            'username': 'admin_test',
            'password': 'senhaforte123'
        })
        return response.json['access_token']
    
    def test_create_user(self):
        """Testar criação de usuário"""
        token = self._login_admin()
        
        response = self.client.post('/users', json={
            'username': 'novo_usuario',
            'email': 'novo@teste.com',
            'password': 'senhaforte123',
            'role': 'Visualizador'
        }, headers={
            'Authorization': f'Bearer {token}'
        })
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['user']['username'], 'novo_usuario')
    
    def test_update_user(self):
        """Testar atualização de usuário"""
        token = self._login_admin()
        
        # Primeiro criar usuário
        create_response = self.client.post('/users', json={
            'username': 'usuario_update',
            'email': 'update@teste.com',
            'password': 'senhaforte123'
        }, headers={
            'Authorization': f'Bearer {token}'
        })
        user_id = create_response.json['user']['id']
        
        # Atualizar usuário
        update_response = self.client.put(f'/users/{user_id}', json={
            'username': 'usuario_atualizado',
            'email': 'atualizado@teste.com'
        }, headers={
            'Authorization': f'Bearer {token}'
        })
        
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json['user']['username'], 'usuario_atualizado')
    
    def test_delete_user(self):
        """Testar exclusão de usuário"""
        token = self._login_admin()
        
        # Primeiro criar usuário
        create_response = self.client.post('/users', json={
            'username': 'usuario_delete',
            'email': 'delete@teste.com',
            'password': 'senhaforte123'
        }, headers={
            'Authorization': f'Bearer {token}'
        })
        user_id = create_response.json['user']['id']
        
        # Excluir usuário
        delete_response = self.client.delete(f'/users/{user_id}', 
            headers={
                'Authorization': f'Bearer {token}'
            }
        )
        
        self.assertEqual(delete_response.status_code, 200)
    
    def test_list_users(self):
        """Testar listagem de usuários"""
        token = self._login_admin()
        
        # Criar alguns usuários
        for i in range(3):
            self.client.post('/users', json={
                'username': f'usuario_{i}',
                'email': f'usuario{i}@teste.com',
                'password': 'senhaforte123'
            }, headers={
                'Authorization': f'Bearer {token}'
            })
        
        # Listar usuários
        response = self.client.get('/users', 
            headers={
                'Authorization': f'Bearer {token}'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json['users']) > 0)

if __name__ == '__main__':
    unittest.main()
