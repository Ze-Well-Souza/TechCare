import unittest
import os
import tempfile
from app import create_app
from app.models.user import User
from app.models.role import Role
from app.services.backup_service import BackupService
from app.extensions import db
import json

class BackupTestCase(unittest.TestCase):
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
                permissions=['SYSTEM_BACKUP']
            )
            db.session.add(admin_role)
            
            # Criar usuário admin para testes
            admin_user = User(
                username='admin_backup', 
                email='admin_backup@test.com', 
                password='senhaforte123',
                role=admin_role
            )
            db.session.add(admin_user)
            db.session.commit()
    
    def _login_admin(self):
        """Realizar login como admin"""
        response = self.client.post('/auth/login', json={
            'username': 'admin_backup',
            'password': 'senhaforte123'
        })
        return response.json['access_token']
    
    def test_create_database_backup(self):
        """Testar criação de backup de banco de dados"""
        token = self._login_admin()
        
        response = self.client.post('/system/backup/database', 
            headers={
                'Authorization': f'Bearer {token}'
            },
            json={
                'description': 'Backup de teste'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue('backup_file' in response.json)
        self.assertTrue('backup_path' in response.json)
    
    def test_create_file_backup(self):
        """Testar criação de backup de arquivos"""
        token = self._login_admin()
        
        response = self.client.post('/system/backup/files', 
            headers={
                'Authorization': f'Bearer {token}'
            },
            json={
                'directories': ['app', 'config'],
                'description': 'Backup de arquivos de teste'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue('backup_file' in response.json)
        self.assertTrue('backup_path' in response.json)
    
    def test_list_backups(self):
        """Testar listagem de backups"""
        token = self._login_admin()
        
        # Primeiro criar alguns backups
        self.client.post('/system/backup/database', 
            headers={
                'Authorization': f'Bearer {token}'
            }
        )
        self.client.post('/system/backup/files', 
            headers={
                'Authorization': f'Bearer {token}'
            }
        )
        
        # Listar backups
        response = self.client.get('/system/backup/list', 
            headers={
                'Authorization': f'Bearer {token}'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json['backups']) > 0)
    
    def test_restore_database_backup(self):
        """Testar restauração de backup de banco de dados"""
        token = self._login_admin()
        
        # Primeiro criar backup
        backup_response = self.client.post('/system/backup/database', 
            headers={
                'Authorization': f'Bearer {token}'
            }
        )
        backup_file = backup_response.json['backup_file']
        
        # Restaurar backup
        restore_response = self.client.post('/system/backup/restore/database', 
            headers={
                'Authorization': f'Bearer {token}'
            },
            json={
                'backup_file': backup_file
            }
        )
        
        self.assertEqual(restore_response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
