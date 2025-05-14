from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models.diagnostic import Diagnostic
from app.services.diagnostic_service import DiagnosticService
from app import db
import json

# Cria o blueprint
diagnostic_overview = Blueprint('diagnostic_overview', __name__)

@diagnostic_overview.route('/')
@login_required
def index():
    """Rota da página de visão geral de diagnóstico"""
    try:
        # Inicializa o serviço de diagnóstico
        diagnostic_service = DiagnosticService()
        
        # Obtém informações resumidas do sistema e hardware do computador
        system_info = diagnostic_service.get_system_summary()
        
        # Obtém o último diagnóstico do usuário, se existir
        user_diagnostics = diagnostic_service.get_diagnostic_history(current_user.id, 1)
        last_diagnostic = user_diagnostics[0] if user_diagnostics else None
        
        return render_template('diagnostic/overview.html', 
                               system_info=system_info,
                               last_diagnostic=last_diagnostic)
    except Exception as e:
        return render_template('diagnostic/overview.html', 
                               error=str(e),
                               system_info={},
                               last_diagnostic=None)

@diagnostic_overview.route('/results/<int:diagnostic_id>')
@login_required
def view_results(diagnostic_id):
    try:
        diagnostic_model = db.session.get(Diagnostic, diagnostic_id)
        if not diagnostic_model:
            return render_template('errors/404.html', message="Diagnóstico não encontrado"), 404
        if diagnostic_model.user_id != current_user.id and not current_user.is_admin() and not current_user.is_technician():
            return render_template('errors/403.html', message="Você não tem permissão para acessar este diagnóstico"), 403
        results = {
            'id': diagnostic_model.id,
            'name': diagnostic_model.name,
            'date': diagnostic_model.date.strftime('%d/%m/%Y %H:%M'),
            'score': diagnostic_model.score,
            'status': diagnostic_model.status,
            'cpu': diagnostic_model.get_cpu_results(),
            'memory': diagnostic_model.get_memory_results(),
            'disk': diagnostic_model.get_disk_results(),
            'startup': diagnostic_model.get_startup_results(),
            'drivers': diagnostic_model.get_driver_results(),
            'security': diagnostic_model.get_security_results(),
            'network': diagnostic_model.get_network_results(),
            'recommendations': json.loads(diagnostic_model.recommendations) if diagnostic_model.recommendations else [],
            'problems': json.loads(diagnostic_model.notes) if diagnostic_model.notes else []
        }
        response_format = request.args.get('format', 'html')
        if response_format == 'json':
            return jsonify(results)
        else:
            return render_template('diagnostic/results.html', results=results)
    except Exception as e:
        return render_template('errors/500.html', message=str(e)), 500

@diagnostic_overview.route('/history')
@login_required
def history():
    if current_user.is_admin():
        diagnostics = Diagnostic.query.order_by(Diagnostic.date.desc()).all()
    else:
        diagnostics = Diagnostic.query.filter_by(user_id=current_user.id).order_by(Diagnostic.date.desc()).all()
    response_format = request.args.get('format', 'html')
    if response_format == 'json':
        return jsonify([{
            'id': diag.id,
            'name': diag.name,
            'date': diag.date.strftime('%d/%m/%Y %H:%M'),
            'score': diag.score,
            'status': diag.status
        } for diag in diagnostics])
    else:
        return render_template('diagnostic/history.html', diagnostics=diagnostics)

@diagnostic_overview.route('/computer-identity')
@login_required
def computer_identity():
    """Exibe as informações detalhadas do computador (RG do Computador)"""
    try:
        # Inicializa o serviço de diagnóstico
        diagnostic_service = DiagnosticService()
        
        # Obtém informações detalhadas do computador
        computer_info = diagnostic_service.get_computer_identity()
        
        # Determina o formato da resposta
        response_format = request.args.get('format', 'html')
        
        if response_format == 'json':
            return jsonify({
                'success': True,
                'data': computer_info
            })
        else:
            return render_template('diagnostic/computer_identity.html', computer_info=computer_info)
    except Exception as e:
        return render_template('errors/500.html', message=str(e)), 500 