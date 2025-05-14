import unittest
import re
from app import create_app
from app.models.user import User
from app.models.role import Role
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

class SecurityTestCase(unittest.TestCase):
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
                username='admin_security', 
                email='admin_security@test.com', 
                password='senhaforte123',
                role=admin_role
            )
            db.session.add(admin_user)
            db.session.commit()
    
    def test_password_hashing(self):
        """Testar hashing de senhas"""
        # Gerar senha
        raw_password = 'senhaforte123'
        
        # Gerar hash
        password_hash = generate_password_hash(raw_password)
        
        # Verificar hash
        self.assertTrue(check_password_hash(password_hash, raw_password))
        self.assertFalse(check_password_hash(password_hash, 'senhadiferente'))
    
    def test_input_validation(self):
        """Testar validação de entrada"""
        # Testar criação de usuário com dados inválidos
        response = self.client.post('/users', json={
            'username': 'user<script>alert("xss")</script>',
            'email': 'invalid-email',
            'password': 'short'
        })
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
    
    def test_sql_injection_prevention(self):
        """Testar prevenção de injeção de SQL"""
        # Tentar injeção de SQL no login
        response = self.client.post('/auth/login', json={
            'username': "' OR 1=1 --",
            'password': "' OR 1=1 --"
        })
        
        self.assertEqual(response.status_code, 401)
    
    def test_sensitive_data_encryption(self):
        """Testar criptografia de dados sensíveis"""
        # Criar usuário com dados sensíveis
        response = self.client.post('/users', json={
            'username': 'sensitive_user',
            'email': 'sensitive@test.com',
            'password': 'senhaforte123',
            'sensitive_data': {
                'cpf': '123.456.789-00',
                'credit_card': '1234-5678-9012-3456'
            }
        })
        
        self.assertEqual(response.status_code, 201)
        
        # Verificar se dados sensíveis estão criptografados no banco
        user = User.query.filter_by(username='sensitive_user').first()
        
        # Verificar que dados sensíveis não estão em texto plano
        self.assertNotEqual(user.sensitive_data, {
            'cpf': '123.456.789-00',
            'credit_card': '1234-5678-9012-3456'
        })
    
    def test_brute_force_protection(self):
        """Testar proteção contra tentativas de login em massa"""
        # Simular múltiplas tentativas de login
        for _ in range(10):
            response = self.client.post('/auth/login', json={
                'username': 'admin_security',
                'password': 'senhaerrada'
            })
        
        # Última tentativa deve ser bloqueada
        self.assertEqual(response.status_code, 429)  # Too Many Requests
    
    def test_secure_token_generation(self):
        """Testar geração de tokens seguros"""
        # Login para obter token
        login_response = self.client.post('/auth/login', json={
            'username': 'admin_security',
            'password': 'senhaforte123'
        })
        
        token = login_response.json['access_token']
        
        # Verificar características do token
        self.assertTrue(len(token) > 50)  # Token deve ser suficientemente longo
        
        # Verificar se o token segue padrões de segurança
        # Exemplo: token deve conter caracteres aleatórios
        self.assertTrue(re.match(r'^[A-Za-z0-9_\-\.]+$', token))

if __name__ == '__main__':
    unittest.main()
