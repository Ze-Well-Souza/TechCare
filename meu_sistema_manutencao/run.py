import os
from app import create_app, db

app = create_app(os.getenv('FLASK_CONFIG', 'default'))

@app.cli.command('create-db')
def create_db():
    """Cria o banco de dados."""
    db.create_all()
    print("Banco de dados criado com sucesso!")

@app.cli.command('create-admin')
def create_admin():
    """Cria um usuário administrador."""
    from app.models import User
    from getpass import getpass
    
    nome = input("Nome do admin: ")
    email = input("Email do admin: ")
    senha = getpass("Senha do admin: ")
    
    admin = User(nome=nome, email=email, is_admin=True)
    admin.set_password(senha)
    
    db.session.add(admin)
    db.session.commit()
    
    print(f"Admin {nome} criado com sucesso!")

if __name__ == '__main__':
    app.run()
