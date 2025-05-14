from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import Session
from src.models.user import User, UserRole
from datetime import datetime, timedelta
import jwt
import os

class AuthService:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.secret_key = os.getenv('SECRET_KEY', 'fallback_secret_key')

    def create_user(self, username: str, email: str, password: str, role: UserRole):
        """Cria um novo usuário no sistema"""
        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            role=role
        )
        self.db.add(new_user)
        self.db.commit()
        return new_user

    def authenticate_user(self, username: str, password: str):
        """Autentica um usuário"""
        user = self.db.query(User).filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            user.last_login = datetime.utcnow()
            self.db.commit()
            return user
        return None

    def generate_token(self, user: User, expires_delta: int = 60):
        """Gera um token JWT para o usuário"""
        to_encode = {
            'sub': user.username,
            'role': user.role.value,
            'exp': datetime.utcnow() + timedelta(minutes=expires_delta)
        }
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm='HS256')
        return encoded_jwt

    def validate_token(self, token: str):
        """Valida um token JWT"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            username = payload.get('sub')
            user = self.db.query(User).filter_by(username=username).first()
            return user
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def change_password(self, user: User, old_password: str, new_password: str):
        """Altera a senha do usuário"""
        if check_password_hash(user.password_hash, old_password):
            user.password_hash = generate_password_hash(new_password)
            self.db.commit()
            return True
        return False
