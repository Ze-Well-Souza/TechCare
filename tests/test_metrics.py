import unittest
import time
from app import create_app
from app.models.user import User
from app.models.role import Role
from app.services.dashboard_service import DashboardService
from app.extensions import db
import psutil

class MetricsTestCase(unittest.TestCase):
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
                permissions=['DASHBOARD_READ']
            )
            db.session.add(admin_role)
            
            # Criar usuários de teste
            for i in range(5):
                user = User(
                    username=f'user_{i}', 
                    email=f'user_{i}@test.com',
                    password='senhaforte123',
                    role=admin_role
                )
                db.session.add(user)
            
            db.session.commit()
    
    def _login_admin(self):
        """Realizar login como admin"""
        response = self.client.post('/auth/login', json={
            'username': 'user_0',
            'password': 'senhaforte123'
        })
        return response.json['access_token']
    
    def test_system_resource_metrics(self):
        """Testar métricas de recursos do sistema"""
        token = self._login_admin()
        
        response = self.client.get('/dashboard/system-resources', 
            headers={
                'Authorization': f'Bearer {token}'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        metrics = response.json
        
        # Verificar métricas de CPU
        self.assertIn('cpu_usage', metrics)
        self.assertTrue(0 <= metrics['cpu_usage'] <= 100)
        
        # Verificar métricas de memória
        self.assertIn('memory_usage', metrics)
        self.assertTrue(0 <= metrics['memory_usage'] <= 100)
        
        # Verificar métricas de disco
        self.assertIn('disk_usage', metrics)
        self.assertTrue(0 <= metrics['disk_usage'] <= 100)
    
    def test_user_metrics(self):
        """Testar métricas de usuários"""
        token = self._login_admin()
        
        response = self.client.get('/dashboard/user-metrics', 
            headers={
                'Authorization': f'Bearer {token}'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        metrics = response.json
        
        # Verificar métricas de usuários
        self.assertIn('total_users', metrics)
        self.assertIn('users_by_role', metrics)
        self.assertEqual(metrics['total_users'], 5)
    
    def test_service_performance_metrics(self):
        """Testar métricas de performance de serviços"""
        token = self._login_admin()
        
        response = self.client.get('/dashboard/service-performance', 
            headers={
                'Authorization': f'Bearer {token}'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        metrics = response.json
        
        # Verificar métricas de performance de serviços
        self.assertIn('services', metrics)
        for service in metrics['services']:
            self.assertIn('name', service)
            self.assertIn('response_time', service)
            self.assertIn('status', service)
    
    def test_audit_log_metrics(self):
        """Testar métricas de logs de auditoria"""
        token = self._login_admin()
        
        # Primeiro gerar alguns logs de auditoria
        self.client.post('/users', json={
            'username': 'new_user',
            'email': 'new_user@test.com',
            'password': 'senhaforte123'
        }, headers={
            'Authorization': f'Bearer {token}'
        })
        
        response = self.client.get('/dashboard/audit-logs', 
            headers={
                'Authorization': f'Bearer {token}'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        metrics = response.json
        
        # Verificar métricas de logs de auditoria
        self.assertIn('total_logs', metrics)
        self.assertIn('logs_by_type', metrics)
        self.assertTrue(metrics['total_logs'] > 0)

if __name__ == '__main__':
    unittest.main()
