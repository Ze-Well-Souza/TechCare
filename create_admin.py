from app import create_app
from app.models.user_repository import UserRepository
from datetime import datetime, UTC

def create_admin_user():
    # Inicializa a aplicação
    app = create_app('development')
    
    # Cria um contexto de aplicação
    with app.app_context():
        # Inicializa o repositório de usuários
        user_repository = UserRepository()
        
        # Verifica se já existe um administrador
        admin = user_repository.get_one_by(role='admin')
        
        if admin:
            print(f"Um administrador já existe: {admin.username}")
            return
        
        try:
            # Cria um novo usuário administrador usando o repositório
            admin = user_repository.register_user(
                username='admin',
                email='admin@techcare.com',
                name='Administrador',
                password='admin123',  # Esta senha deve ser alterada após o primeiro login # zetech123!
                role='admin'
            )
            
            print(f"Administrador criado com sucesso!")
            print(f"Username: admin")
            print(f"Senha: admin123")
            print(f"IMPORTANTE: Altere esta senha após o primeiro login!")
        except ValueError as e:
            print(f"Erro ao criar administrador: {e}")

if __name__ == "__main__":
    create_admin_user() 