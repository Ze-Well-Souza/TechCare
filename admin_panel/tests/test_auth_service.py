import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.user import Base, User, UserRole
from src.services.auth_service import AuthService

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
def auth_service(dbsession):
    return AuthService(dbsession)

def test_create_user(auth_service, dbsession):
    user = auth_service.create_user(
        username='test_user', 
        email='test@example.com', 
        password='secure_password', 
        role=UserRole.ADMIN_TECNICO
    )
    
    assert user.username == 'test_user'
    assert user.role == UserRole.ADMIN_TECNICO

def test_authenticate_user(auth_service, dbsession):
    # Primeiro, cria um usuário
    auth_service.create_user(
        username='login_user', 
        email='login@example.com', 
        password='correct_password', 
        role=UserRole.VISUALIZADOR
    )

    # Tenta autenticar com senha correta
    authenticated_user = auth_service.authenticate_user('login_user', 'correct_password')
    assert authenticated_user is not None
    assert authenticated_user.username == 'login_user'

    # Tenta autenticar com senha incorreta
    failed_auth = auth_service.authenticate_user('login_user', 'wrong_password')
    assert failed_auth is None

def test_generate_and_validate_token(auth_service, dbsession):
    # Cria um usuário
    user = auth_service.create_user(
        username='token_user', 
        email='token@example.com', 
        password='token_password', 
        role=UserRole.ADMIN_MASTER
    )

    # Gera token
    token = auth_service.generate_token(user)
    assert token is not None

    # Valida token
    validated_user = auth_service.validate_token(token)
    assert validated_user is not None
    assert validated_user.username == 'token_user'

def test_change_password(auth_service, dbsession):
    # Cria um usuário
    user = auth_service.create_user(
        username='change_pass_user', 
        email='changepass@example.com', 
        password='old_password', 
        role=UserRole.ADMIN_TECNICO
    )

    # Tenta mudar a senha com senha antiga correta
    result = auth_service.change_password(user, 'old_password', 'new_password')
    assert result is True

    # Verifica se a nova senha funciona
    authenticated_user = auth_service.authenticate_user('change_pass_user', 'new_password')
    assert authenticated_user is not None

    # Tenta mudar a senha com senha antiga incorreta
    result = auth_service.change_password(user, 'wrong_old_password', 'another_new_password')
    assert result is False
