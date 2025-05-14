import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.user import Base, User, UserRole

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
    """Returns an sqlalchemy session, and after the test tears down everything properly."""
    connection = engine.connect()
    # begin the nested transaction
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    # roll back the broader transaction
    transaction.rollback()
    # close the connection
    connection.close()

def test_create_user(dbsession):
    new_user = User(
        username='admin_test', 
        email='admin@techcare.com', 
        password_hash='hashed_password', 
        role=UserRole.ADMIN_MASTER
    )
    dbsession.add(new_user)
    dbsession.commit()

    assert new_user.id is not None
    assert new_user.username == 'admin_test'
    assert new_user.role == UserRole.ADMIN_MASTER

def test_user_roles():
    roles = [role.value for role in UserRole]
    assert set(roles) == {'admin_master', 'admin_tecnico', 'visualizador'}

def test_unique_constraints(dbsession):
    user1 = User(
        username='unique_user', 
        email='unique@email.com', 
        password_hash='hash1', 
        role=UserRole.ADMIN_TECNICO
    )
    dbsession.add(user1)
    dbsession.commit()

    with pytest.raises(Exception):
        user2 = User(
            username='unique_user', 
            email='another@email.com', 
            password_hash='hash2', 
            role=UserRole.VISUALIZADOR
        )
        dbsession.add(user2)
        dbsession.commit()
