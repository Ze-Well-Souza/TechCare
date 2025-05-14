import pytest
from flask_testing import TestCase
from app import create_app
from app.models import User
from app.extensions import db

class IntegrationTestCase(TestCase):
    def create_app(self):
        app = create_app('testing')
        return app

    def setUp(self):
        db.create_all()
        # Criar usuário de teste
        test_user = User(username='admin_test', email='admin@test.com')
        test_user.set_password('test_password')
        db.session.add(test_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_user_authentication_flow(self):
        # Teste de fluxo completo de autenticação
        # 1. Verificar criação de usuário
        user = User.query.filter_by(username='admin_test').first()
        assert user is not None
        assert user.username == 'admin_test'

        # 2. Testar autenticação
        with self.client:
            response = self.client.post('/auth/login', data={
                'username': 'admin_test',
                'password': 'test_password'
            }, follow_redirects=True)
            assert response.status_code == 200
            # Adicionar verificações específicas de autorização

    def test_dashboard_access(self):
        # Teste de acesso ao dashboard
        with self.client:
            # Primeiro, fazer login
            self.client.post('/auth/login', data={
                'username': 'admin_test',
                'password': 'test_password'
            })
            
            # Tentar acessar dashboard
            response = self.client.get('/dashboard')
            assert response.status_code == 200
            # Verificar conteúdo do dashboard

    def test_user_management_integration(self):
        # Teste de integração de gerenciamento de usuários
        with self.client:
            # Login
            self.client.post('/auth/login', data={
                'username': 'admin_test',
                'password': 'test_password'
            })

            # Criar novo usuário
            response = self.client.post('/users/create', data={
                'username': 'new_admin',
                'email': 'new_admin@test.com',
                'password': 'new_password',
                'role': 'admin'
            })
            assert response.status_code in [200, 302]  # Sucesso ou redirecionamento

            # Verificar se usuário foi criado
            new_user = User.query.filter_by(username='new_admin').first()
            assert new_user is not None
            assert new_user.email == 'new_admin@test.com'

if __name__ == '__main__':
    pytest.main([__file__])
