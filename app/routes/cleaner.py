from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user

cleaner = Blueprint('cleaner', __name__)

# Importa submódulos de rotas
from . import cleaner_cleaning
from . import cleaner_analysis
from . import cleaner_maintenance
from . import cleaner_startup
from app.models.maintenance_plan import MaintenancePlan
from app import db

@cleaner.route('/')
@login_required
def index():
    """Rota principal de limpeza"""
    return render_template('cleaner/index.html')

@cleaner.route('/maintenance_plans')
@login_required
def maintenance_plans_list():
    """Lista todos os planos de manutenção do usuário logado"""
    plans = MaintenancePlan.query.filter_by(user_id=current_user.id).order_by(MaintenancePlan.created_at.desc()).all()
    # Separar planos ativos e inativos
    active_plans = [p for p in plans if p.enabled]
    inactive_plans = [p for p in plans if not p.enabled]
    # Histórico simulado (deve ser integrado ao histórico real de execuções)
    maintenance_history = []
    # Status do sistema simulado (pode ser integrado ao CleanerService futuramente)
    system_status = {
        'optimization_level': 80,
        'temp_status': 'good',
        'browser_status': 'warning',
        'registry_status': 'good',
        'disk_status': 'good',
    }
    return render_template('cleaner/maintenance_plans.html', 
        active_plans=active_plans, 
        inactive_plans=inactive_plans, 
        maintenance_history=maintenance_history, 
        system_status=system_status, 
        title="Planos de Manutenção")

@cleaner.route('/maintenance_plans/new', methods=['GET', 'POST'])
@login_required
def maintenance_plan_create():
    """Cria um novo plano de manutenção"""
    if request.method == 'POST':
        name = request.form.get('name')
        cleaning_types = ','.join(request.form.getlist('cleaning_types'))
        frequency = request.form.get('frequency')
        day_of_week = request.form.get('day_of_week')
        day_of_month = request.form.get('day_of_month')
        
        # Usar a string do tempo diretamente ao invés de convertê-la para um objeto time
        time_str = request.form.get('time')
        
        notify_email = request.form.get('notify_email')
        notify_sms = request.form.get('notify_sms')
        enabled = bool(request.form.get('enabled', True))
        plan = MaintenancePlan(
            user_id=current_user.id,
            name=name,
            cleaning_types=cleaning_types,
            frequency=frequency,
            day_of_week=day_of_week or None,
            day_of_month=int(day_of_month) if day_of_month else None,
            time=time_str,
            notify_email=notify_email,
            notify_sms=notify_sms,
            enabled=enabled
        )
        db.session.add(plan)
        db.session.commit()
        flash('Plano de manutenção criado com sucesso!', 'success')
        return redirect(url_for('cleaner.maintenance_plans_list'))
    return render_template('cleaner/maintenance_plan_form.html', plan=None, title="Novo Plano de Manutenção")

@cleaner.route('/maintenance_plans/<int:plan_id>/edit', methods=['GET', 'POST'])
@login_required
def maintenance_plan_edit(plan_id):
    plan = MaintenancePlan.query.filter_by(id=plan_id, user_id=current_user.id).first_or_404()
    if request.method == 'POST':
        plan.name = request.form.get('name')
        plan.cleaning_types = ','.join(request.form.getlist('cleaning_types'))
        plan.frequency = request.form.get('frequency')
        plan.day_of_week = request.form.get('day_of_week')
        plan.day_of_month = int(request.form.get('day_of_month')) if request.form.get('day_of_month') else None
        
        # Usar a string do tempo diretamente sem converter para objeto time
        plan.time = request.form.get('time')
        
        plan.notify_email = request.form.get('notify_email')
        plan.notify_sms = request.form.get('notify_sms')
        plan.enabled = bool(request.form.get('enabled', True))
        db.session.commit()
        flash('Plano de manutenção atualizado com sucesso!', 'success')
        return redirect(url_for('cleaner.maintenance_plans_list'))
    return render_template('cleaner/maintenance_plan_form.html', plan=plan, title="Editar Plano de Manutenção")

@cleaner.route('/maintenance_plans/<int:plan_id>/delete', methods=['POST'])
@login_required
def maintenance_plan_delete(plan_id):
    plan = MaintenancePlan.query.filter_by(id=plan_id, user_id=current_user.id).first_or_404()
    db.session.delete(plan)
    db.session.commit()
    flash('Plano de manutenção removido com sucesso!', 'success')
    return redirect(url_for('cleaner.maintenance_plans_list'))

@cleaner.route('/maintenance_plans/<int:plan_id>')
@login_required
def maintenance_plan_detail(plan_id):
    plan = MaintenancePlan.query.filter_by(id=plan_id, user_id=current_user.id).first_or_404()
    return render_template('cleaner/maintenance_plan_detail.html', plan=plan, title=f"Plano: {plan.name}") 