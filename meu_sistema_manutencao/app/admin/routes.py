from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import admin
from .forms import UserManagementForm
from .. import db
from ..models import User, Log, Machine, PLANOS

@admin.route('/')
@login_required
def index():
    """Painel principal do admin."""
    if not current_user.is_admin:
        flash('Acesso negado. Área restrita a administradores.', 'danger')
        return redirect(url_for('client.dashboard'))
    
    # Métricas
    total_users = User.query.count()
    users_by_plan = {
        plano: User.query.filter_by(plano=plano).count() 
        for plano in PLANOS.keys()
    }
    total_logs = Log.query.count()
    total_machines = Machine.query.count()
    
    return render_template('admin/index.html', 
                           total_users=total_users, 
                           users_by_plan=users_by_plan,
                           total_logs=total_logs,
                           total_machines=total_machines)

@admin.route('/users')
@login_required
def users():
    """Listar todos os usuários."""
    if not current_user.is_admin:
        flash('Acesso negado. Área restrita a administradores.', 'danger')
        return redirect(url_for('client.dashboard'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    users = User.query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/users.html', users=users)

@admin.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def manage_user(user_id):
    """Gerenciar detalhes de um usuário."""
    if not current_user.is_admin:
        flash('Acesso negado. Área restrita a administradores.', 'danger')
        return redirect(url_for('client.dashboard'))
    
    user = User.query.get_or_404(user_id)
    form = UserManagementForm(obj=user)
    
    if form.validate_on_submit():
        # Log de alteração
        changes = []
        
        if user.plano != form.plano.data:
            changes.append(f'Plano alterado de {user.plano} para {form.plano.data}')
            user.plano = form.plano.data
        
        if user.is_active != form.is_active.data:
            changes.append(f'Status de ativação alterado para {"Ativo" if form.is_active.data else "Inativo"}')
            user.is_active = form.is_active.data
        
        if changes:
            log = Log(
                user_id=current_user.id, 
                acao='editar_usuario', 
                detalhes=f'Usuário {user.nome} modificado: {"; ".join(changes)}'
            )
            db.session.add(log)
        
        db.session.commit()
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/manage_user.html', form=form, user=user)

@admin.route('/logs')
@login_required
def system_logs():
    """Visualizar logs do sistema."""
    if not current_user.is_admin:
        flash('Acesso negado. Área restrita a administradores.', 'danger')
        return redirect(url_for('client.dashboard'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    logs = Log.query.order_by(Log.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/logs.html', logs=logs)
