from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, UTC, timedelta
from uuid import uuid4

from app import db
from app.models.user import User
from app.models.user_repository import UserRepository

auth = Blueprint('auth', __name__)
user_repository = UserRepository()

# Dicionário temporário para tokens de redefinição (em produção, usar banco ou cache)
reset_tokens = {}

@auth.route('/login', methods=['GET', 'POST'])
@auth.route('/auth/login', methods=['GET', 'POST'])  # Rota alternativa para compatibilidade
def login():
    """Rota para login de usuários"""
    # Se o usuário já está autenticado, redireciona para página inicial
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Se for uma requisição POST, processa o login
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        # Valida os dados de entrada
        if not username or not password:
            flash('Por favor, preencha todos os campos.', 'danger')
            return render_template('auth/login.html')
        
        # Busca o usuário pelo nome de usuário
        user = User.query.filter_by(username=username).first()
        
        # Verifica se o usuário existe e a senha está correta
        if user and user.check_password(password):
            # Faz o login do usuário
            login_user(user, remember=remember)
            
            # Redireciona para a página solicitada originalmente ou para a página inicial
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        
        # Se o login falhar, mostra uma mensagem de erro
        flash('Nome de usuário ou senha incorretos.', 'danger')
    
    # Se for uma requisição GET, renderiza o formulário de login
    return render_template('auth/login.html')

@auth.route('/logout')
@auth.route('/auth/logout')  # Rota alternativa para compatibilidade
@login_required
def logout():
    """Rota para logout de usuários"""
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
@auth.route('/auth/register', methods=['GET', 'POST'])  # Rota alternativa para compatibilidade
def register():
    """Rota para registro de novos usuários"""
    # Se o usuário já está autenticado, redireciona para página inicial
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Se for uma requisição POST, processa o registro
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Valida os dados de entrada
        if not username or not email or not password or not confirm_password:
            flash('Por favor, preencha todos os campos.', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('As senhas não coincidem.', 'danger')
            return render_template('auth/register.html')
        
        # Verifica se o nome de usuário já existe
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Este nome de usuário já está em uso.', 'danger')
            return render_template('auth/register.html')
        
        # Verifica se o e-mail já existe
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Este e-mail já está cadastrado.', 'danger')
            return render_template('auth/register.html')
        
        # Cria o novo usuário
        new_user = User(username=username, email=email)
        new_user.password = password
        
        # Salva o usuário no banco de dados
        db.session.add(new_user)
        db.session.commit()
        
        # Redireciona para a página de login com mensagem de sucesso
        flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('auth.login'))
    
    # Se for uma requisição GET, renderiza o formulário de registro
    return render_template('auth/register.html')

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Rota para visualização e edição do perfil do usuário"""
    if request.method == 'POST':
        # Atualiza as informações do usuário
        name = request.form.get('name')
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        # Verifica se o email já está em uso por outro usuário
        if email != current_user.email and user_repository.exists(email=email):
            flash('Email já está em uso por outro usuário.', 'danger')
            return redirect(url_for('auth.profile'))
        
        update_data = {
            'name': name,
            'email': email
        }
        
        # Se o usuário quiser alterar a senha
        if current_password and new_password:
            if not current_user.verify_password(current_password):
                flash('Senha atual incorreta.', 'danger')
                return redirect(url_for('auth.profile'))
                
            current_user.password = new_password
            flash('Senha atualizada com sucesso.', 'success')
        
        # Atualiza o usuário usando o repositório
        user_repository.update(current_user, **update_data)
        flash('Perfil atualizado com sucesso.', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html')

# Rota para administradores gerenciarem usuários
@auth.route('/admin/users')
@login_required
def admin_users():
    """Rota para administradores gerenciarem usuários"""
    # Verifica se o usuário é administrador
    if not current_user.is_admin():
        flash('Acesso negado. Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('main.index'))
    
    users = user_repository.get_all()
    return render_template('auth/admin_users.html', users=users)

# Rota para administradores editarem usuários
@auth.route('/admin/users/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_user(id):
    """Rota para administradores editarem usuários"""
    # Verifica se o usuário é administrador
    if not current_user.is_admin():
        flash('Acesso negado. Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('main.index'))
    
    user = user_repository.get_by_id(id)
    if not user:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('auth.admin_users'))
    
    if request.method == 'POST':
        # Prepara os dados para atualização
        update_data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'role': request.form.get('role'),
            'active': request.form.get('active') == 'on'
        }
        
        # Se o administrador quiser redefinir a senha do usuário
        new_password = request.form.get('new_password')
        if new_password:
            user.password = new_password
            flash(f'Senha do usuário {user.username} redefinida com sucesso.', 'success')
        
        # Atualiza o usuário usando o repositório
        user_repository.update(user, **update_data)
        flash(f'Usuário {user.username} atualizado com sucesso.', 'success')
        return redirect(url_for('auth.admin_users'))
    
    return render_template('auth/admin_edit_user.html', user=user)

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Se o e-mail estiver cadastrado, você receberá instruções para redefinir sua senha.', 'info')
            return render_template('auth/forgot_password.html')
        # Gera token e armazena com expiração
        token = str(uuid4())
        reset_tokens[token] = {'user_id': user.id, 'expires': datetime.utcnow() + timedelta(hours=1)}
        # Simula envio de e-mail
        flash(f'Um link para redefinir sua senha foi enviado para {email}. (Token: {token})', 'success')
        return render_template('auth/forgot_password.html')
    return render_template('auth/forgot_password.html')

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    token_data = reset_tokens.get(token)
    if not token_data or token_data['expires'] < datetime.utcnow():
        flash('Token inválido ou expirado. Solicite uma nova redefinição.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if not password or not confirm_password:
            flash('Preencha todos os campos.', 'danger')
            return render_template('auth/reset_password.html', token=token)
        if password != confirm_password:
            flash('As senhas não coincidem.', 'danger')
            return render_template('auth/reset_password.html', token=token)
        # Atualiza a senha do usuário
        user = User.query.get(token_data['user_id'])
        if not user:
            flash('Usuário não encontrado.', 'danger')
            return redirect(url_for('auth.forgot_password'))
        user.password = password
        db.session.commit()
        del reset_tokens[token]
        flash('Senha redefinida com sucesso! Faça login com sua nova senha.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', token=token) 