import pytest
from flask_testing import TestCase
from app import create_app, db
from app.models import User, Log, Machine

class BaseTestCase(TestCase):
    def create_app(self):
        app = create_app('testing')
        app.config['TESTING'] = True
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def test_user(test_client):
    """Criar usuário de teste para autenticação."""
    user = User(
        nome='Usuário Teste',
        email='teste@exemplo.com',
        is_admin=False,
        plano='free'
    )
    user.set_password('senha_teste')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture(scope='function')
def test_admin(test_client):
    """Criar usuário administrador de teste."""
    admin = User(
        nome='Admin Teste',
        email='admin@exemplo.com',
        is_admin=True,
        plano='profissional'
    )
    admin.set_password('admin_teste')
    db.session.add(admin)
    db.session.commit()
    return admin

@pytest.fixture(scope='function')
def test_client(request):
    """Criar cliente de teste."""
    test_case = BaseTestCase('run')
    test_case.setUp()
    client = test_case.client
    
    def fin():
        test_case.tearDown()
    
    request.addfinalizer(fin)
    return client
