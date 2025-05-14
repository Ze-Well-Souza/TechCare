import pytest
from app.models.user_repository import UserRepository
from app.models.user import User
from unittest.mock import MagicMock, patch
from datetime import datetime, UTC

@pytest.fixture
def user_repo(monkeypatch):
    repo = UserRepository()
    # Mocka métodos do Repository base para isolar UserRepository
    monkeypatch.setattr(repo, 'get_one_by', lambda **kwargs: None)
    monkeypatch.setattr(repo, 'filter_by', lambda **kwargs: [])
    monkeypatch.setattr(repo, 'save', lambda user: user)
    monkeypatch.setattr(repo, 'exists', lambda **kwargs: False)
    return repo

def test_get_by_username_calls_get_one_by(user_repo, monkeypatch):
    called = {}
    def fake_get_one_by(**kwargs):
        called.update(kwargs)
        return 'user'
    monkeypatch.setattr(user_repo, 'get_one_by', fake_get_one_by)
    result = user_repo.get_by_username('testuser')
    assert result == 'user'
    assert called == {'username': 'testuser'}

def test_get_by_email_calls_get_one_by(user_repo, monkeypatch):
    called = {}
    def fake_get_one_by(**kwargs):
        called.update(kwargs)
        return 'user'
    monkeypatch.setattr(user_repo, 'get_one_by', fake_get_one_by)
    result = user_repo.get_by_email('test@example.com')
    assert result == 'user'
    assert called == {'email': 'test@example.com'}

def test_authenticate_success(user_repo, monkeypatch):
    user = MagicMock()
    user.verify_password.return_value = True
    monkeypatch.setattr(user_repo, 'get_by_username', lambda username: user)
    result = user_repo.authenticate('test', 'pass')
    assert result is user
    user.verify_password.assert_called_once_with('pass')

def test_authenticate_fail_wrong_password(user_repo, monkeypatch):
    user = MagicMock()
    user.verify_password.return_value = False
    monkeypatch.setattr(user_repo, 'get_by_username', lambda username: user)
    result = user_repo.authenticate('test', 'wrong')
    assert result is None
    user.verify_password.assert_called_once_with('wrong')

def test_authenticate_fail_no_user(user_repo, monkeypatch):
    monkeypatch.setattr(user_repo, 'get_by_username', lambda username: None)
    result = user_repo.authenticate('test', 'pass')
    assert result is None

def test_update_last_login_sets_datetime(user_repo, monkeypatch):
    user = MagicMock()
    monkeypatch.setattr(user_repo, 'save', lambda u: u)
    result = user_repo.update_last_login(user)
    assert result is user
    assert isinstance(user.last_login, datetime)

def test_get_active_users_calls_filter_by(user_repo, monkeypatch):
    called = {}
    monkeypatch.setattr(user_repo, 'filter_by', lambda **kwargs: kwargs)
    result = user_repo.get_active_users()
    assert result == {'active': True}

def test_get_by_role_calls_filter_by(user_repo, monkeypatch):
    called = {}
    monkeypatch.setattr(user_repo, 'filter_by', lambda **kwargs: kwargs)
    result = user_repo.get_by_role('admin')
    assert result == {'role': 'admin'}

def test_register_user_success(user_repo, monkeypatch):
    monkeypatch.setattr(user_repo, 'exists', lambda **kwargs: False)
    monkeypatch.setattr(user_repo, 'save', lambda user: user)
    result = user_repo.register_user('u','e','n','p','admin')
    assert isinstance(result, User)
    assert result.username == 'u'
    assert result.email == 'e'
    assert result.name == 'n'
    assert result.role == 'admin'
    assert result.verify_password('p')

def test_register_user_username_exists(user_repo, monkeypatch):
    monkeypatch.setattr(user_repo, 'exists', lambda **kwargs: True if 'username' in kwargs else False)
    with pytest.raises(ValueError):
        user_repo.register_user('u','e','n','p','admin')

def test_register_user_email_exists(user_repo, monkeypatch):
    # username não existe, mas email existe
    def exists(**kwargs):
        if 'username' in kwargs:
            return False
        if 'email' in kwargs:
            return True
        return False
    monkeypatch.setattr(user_repo, 'exists', exists)
    with pytest.raises(ValueError):
        user_repo.register_user('u','e','n','p','admin') 