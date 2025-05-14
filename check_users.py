from app import create_app, db
from app.models.user import User

def main():
    # Inicializa a aplicação
    app = create_app('development')
    
    # Cria um contexto de aplicação
    with app.app_context():
        # Consulta todos os usuários
        users = User.query.all()
        
        # Exibe os usuários existentes
        print("Usuários existentes:")
        if users:
            for user in users:
                print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}, Papel: {user.role}")
        else:
            print("Nenhum usuário encontrado no banco de dados.")

if __name__ == "__main__":
    main() 