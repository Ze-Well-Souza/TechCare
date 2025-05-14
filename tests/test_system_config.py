import unittest
from app import create_app
from app.models.user import User
from app.models.role import Role
from app.extensions import db
import json

class SystemConfigTestCase(unittest.TestCase):
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
                permissions=['SYSTEM_CONFIG']
            )
            db.session.add(admin_role)
            
            # Criar usuário admin para testes
            admin_user = User(
                username='admin_config', 
                email='admin_config@test.com', 
                password='senhaforte123',
                role=admin_role
            )
            db.session.add(admin_user)
            db.session.commit()
    
    def _login_admin(self):
        """Realizar login como admin"""
        response = self.client.post('/auth/login', json={
            'username': 'admin_config',
            'password': 'senhaforte123'
        })
        return response.json['access_token']
    
    def test_create_config(self):
        """Testar criação de configuração"""
        token = self._login_admin()
        
        response = self.client.post('/system/config', json={
            'config_key': 'test_config',
            'config_value': 'test_value',
            'description': 'Configuração de teste'
        }, headers={
            'Authorization': f'Bearer {token}'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['config']['config_key'], 'test_config')
    
    def test_get_config(self):
        """Testar recuperação de configuração"""
        token = self._login_admin()
        
        # Primeiro criar configuração
        self.client.post('/system/config', json={
            'config_key': 'retrieve_config',
            'config_value': 'retrieve_value'
        }, headers={
            'Authorization': f'Bearer {token}'
        })
        
        # Recuperar configuração
        response = self.client.get('/system/config/retrieve_config', 
            headers={
                'Authorization': f'Bearer {token}'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['config_value'], 'retrieve_value')
    
    def test_update_config(self):
        """Testar atualização de configuração"""
        token = self._login_admin()
        
        # Primeiro criar configuração
        self.client.post('/system/config', json={
            'config_key': 'update_config',
            'config_value': 'initial_value'
        }, headers={
            'Authorization': f'Bearer {token}'
        })
        
        # Atualizar configuração
        response = self.client.post('/system/config', json={
            'config_key': 'update_config',
            'config_value': 'updated_value'
        }, headers={
            'Authorization': f'Bearer {token}'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['config']['config_value'], 'updated_value')
    
    def test_delete_config(self):
        """Testar exclusão de configuração"""
        token = self._login_admin()
        
        # Primeiro criar configuração
        self.client.post('/system/config', json={
            'config_key': 'delete_config',
            'config_value': 'delete_value'
        }, headers={
            'Authorization': f'Bearer {token}'
        })
        
        # Excluir configuração
        response = self.client.delete('/system/config/delete_config', 
            headers={
                'Authorization': f'Bearer {token}'
            }
        )
        
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
