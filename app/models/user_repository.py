"""
Módulo que implementa o repositório específico para o modelo User.
"""
from typing import Optional, List
from datetime import datetime, UTC

from app import db
from app.models.user import User
from app.models.repository import Repository

class UserRepository(Repository[User]):
    """Repositório para operações específicas do modelo User"""
    
    def __init__(self):
        super().__init__(User)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Busca um usuário pelo nome de usuário"""
        return self.get_one_by(username=username)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Busca um usuário pelo email"""
        return self.get_one_by(email=email)
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Autentica um usuário com nome de usuário e senha"""
        user = self.get_by_username(username)
        if user and user.verify_password(password):
            return user
        return None
    
    def update_last_login(self, user: User) -> User:
        """Atualiza a data do último login do usuário"""
        user.last_login = datetime.now(UTC)
        return self.save(user)
    
    def get_active_users(self) -> List[User]:
        """Retorna todos os usuários ativos"""
        return self.filter_by(active=True)
    
    def get_by_role(self, role: str) -> List[User]:
        """Retorna todos os usuários com determinado papel"""
        return self.filter_by(role=role)
    
    def register_user(self, username: str, email: str, name: str, 
                      password: str, role: str = 'user') -> User:
        """Registra um novo usuário no sistema"""
        # Verifica se já existe um usuário com o mesmo nome ou email
        if self.exists(username=username):
            raise ValueError("Nome de usuário já existe")
        
        if self.exists(email=email):
            raise ValueError("Email já cadastrado")
        
        # Cria o novo usuário
        user = User(
            username=username,
            email=email,
            name=name,
            role=role
        )
        user.password = password
        
        # Salva o usuário no banco de dados
        return self.save(user) 