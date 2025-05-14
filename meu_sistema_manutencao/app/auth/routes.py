from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .forms import LoginForm, RegistrationForm
from .. import db
from ..models import User
from datetime import datetime

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Redireciona usuário logado
    if current_user.is_authenticated:
        return redirect(url_for('client.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            user.ultimo_login = datetime.utcnow()
            db.session.commit()
            
            # Log de login
            from ..models import Log
            login_log = Log(
                user_id=user.id, 
                acao='login', 
                detalhes='Login bem-sucedido',
                ip_address=request.remote_addr
            )
            db.session.add(login_log)
            db.session.commit()
            
            flash('Login realizado com sucesso!', 'success')
            
            # Redireciona admin para painel admin, outros para dashboard
            return redirect(url_for('admin.index') if user.is_admin else url_for('client.dashboard'))
        
        flash('Email ou senha inválidos', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    # Log de logout
    logout_log = Log(
        user_id=current_user.id, 
        acao='logout', 
        detalhes='Logout realizado',
        ip_address=request.remote_addr
    )
    db.session.add(logout_log)
    db.session.commit()
    
    logout_user()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    # Só admin pode registrar novos usuários
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('Você não tem permissão para registrar novos usuários.', 'danger')
        return redirect(url_for('auth.login'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            nome=form.nome.data,
            email=form.email.data,
            plano=form.plano.data,
            is_admin=form.is_admin.data
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Log de registro
            registro_log = Log(
                user_id=current_user.id, 
                acao='registro_usuario', 
                detalhes=f'Usuário {user.nome} registrado',
                ip_address=request.remote_addr
            )
            db.session.add(registro_log)
            db.session.commit()
            
            flash(f'Usuário {user.nome} registrado com sucesso!', 'success')
            return redirect(url_for('admin.users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar usuário: {str(e)}', 'danger')
    
    return render_template('auth/register.html', form=form)
