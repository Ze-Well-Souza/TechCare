import pytest
from flask import Flask
from flask_jwt_extended import JWTManager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.user import Base, User, UserRole
from src.controllers.user_controller import user_bp, UserController
from src.services.auth_service import AuthService

@pytest.fixture(scope='module')
def app():
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = 'test_secret_key'
    app.config['TESTING'] = True
    JWTManager(app)
    
    app.register_blueprint(user_bp, url_prefix='/user')
    return app

@pytest.fixture(scope='module')
def engine():
    return create_engine('sqlite:///:memory:')

@pytest.fixture(scope='module')
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def dbsession(engine, tables):
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(app, dbsession):
    return app.test_client()

@pytest.fixture
def auth_service(dbsession):
    return AuthService(dbsession)

def test_user_login(client, dbsession, auth_service):
    # Primeiro, cria um usuário
    user = auth_service.create_user(
        username='login_test', 
        email='login@test.com', 
        password='test_password', 
        role=UserRole.ADMIN_MASTER
    )

    # Tenta fazer login
    response = client.post('/user/login', json={
        'username': 'login_test',
        'password': 'test_password'
    })

    assert response.status_code == 200
    assert 'access_token' in response.json

def test_user_registration(client, dbsession, auth_service):
    # Primeiro, cria um usuário admin master
    admin_user = auth_service.create_user(
        username='admin_registrar', 
        email='admin@test.com', 
        password='admin_password', 
        role=UserRole.ADMIN_MASTER
    )

    # Gera token para o admin
    token = auth_service.generate_token(admin_user)

    # Tenta registrar um novo usuário
    response = client.post('/user/register', json={
        'username': 'new_user',
        'email': 'new@test.com',
        'password': 'new_password',
        'role': 'admin_tecnico'
    }, headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 201
    assert 'user_id' in response.json

def test_change_password(client, dbsession, auth_service):
    # Primeiro, cria um usuário
    user = auth_service.create_user(
        username='password_change', 
        email='change@test.com', 
        password='old_password', 
        role=UserRole.ADMIN_TECNICO
    )

    # Gera token para o usuário
    token = auth_service.generate_token(user)

    # Tenta mudar a senha
    response = client.post('/user/change-password', json={
        'old_password': 'old_password',
        'new_password': 'new_password'
    }, headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 200
    assert response.json['msg'] == 'Senha alterada com sucesso'
