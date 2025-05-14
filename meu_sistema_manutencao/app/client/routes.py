from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from . import client
from .forms import MachineDiagnosticForm
from .. import db
from ..models import Machine, Log, PLANOS

@client.route('/dashboard')
@login_required
def dashboard():
    """Painel do cliente."""
    # Recuperar máquinas do usuário
    machines = Machine.query.filter_by(user_id=current_user.id).all()
    
    # Informações do plano atual
    plano_atual = PLANOS.get(current_user.plano, PLANOS['free'])
    
    return render_template('client/dashboard.html', 
                           machines=machines, 
                           plano_atual=plano_atual)

@client.route('/machine/diagnostic/<int:machine_id>', methods=['GET', 'POST'])
@login_required
def machine_diagnostic(machine_id):
    """Realizar diagnóstico de máquina."""
    # Verificar permissão de plano
    if current_user.plano == 'free':
        flash('Seu plano não permite diagnóstico completo.', 'warning')
        return redirect(url_for('client.dashboard'))
    
    machine = Machine.query.get_or_404(machine_id)
    
    # Verificar se a máquina pertence ao usuário
    if machine.user_id != current_user.id:
        flash('Você não tem permissão para diagnosticar esta máquina.', 'danger')
        return redirect(url_for('client.dashboard'))
    
    form = MachineDiagnosticForm()
    
    if form.validate_on_submit():
        # Simular diagnóstico (substituir por script real)
        diagnostic_result = {
            'cpu_usage': form.check_cpu.data,
            'memory_usage': form.check_memory.data,
            'disk_health': form.check_disk.data,
            'network_status': form.check_network.data
        }
        
        # Criar log de diagnóstico
        log = Log(
            user_id=current_user.id,
            acao='diagnostico_maquina',
            detalhes=f'Diagnóstico da máquina {machine.nome}: {diagnostic_result}'
        )
        db.session.add(log)
        
        # Atualizar data do último diagnóstico
        machine.last_diagnostic = datetime.utcnow()
        db.session.commit()
        
        flash('Diagnóstico realizado com sucesso!', 'success')
        return redirect(url_for('client.dashboard'))
    
    return render_template('client/machine_diagnostic.html', 
                           form=form, 
                           machine=machine)
