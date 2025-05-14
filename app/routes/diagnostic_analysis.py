from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
import datetime
from datetime import UTC
from app.services.diagnostic_service import DiagnosticService
from app.services.service_factory import ServiceFactory
from app.models.diagnostic import Diagnostic
from app import db
import json

# Cria o blueprint
diagnostic_analysis = Blueprint('diagnostic_analysis', __name__)

@diagnostic_analysis.route('/run', methods=['GET', 'POST'])
@login_required
def run_diagnostic():
    if request.method == 'GET':
        # Redirecionar para a página de diagnóstico
        return render_template('diagnostic/run_diagnostic.html', user=current_user)
    
    try:
        service = ServiceFactory.get_service(DiagnosticService)
        results = service.run_diagnostics(user_id=str(current_user.id))
        diagnostic_model = Diagnostic(
            user_id=current_user.id,
            name=request.form.get('name', f"Diagnóstico {datetime.datetime.now(UTC).strftime('%d/%m/%Y %H:%M')}"),
            score=results.get('score', 0),
            status=get_status_from_score(results.get('score', 0))
        )
        if 'cpu' in results:
            diagnostic_model.set_cpu_results(results['cpu'])
        if 'memory' in results:
            diagnostic_model.set_memory_results(results['memory'])
        if 'disk' in results:
            diagnostic_model.set_disk_results(results['disk'])
        if 'startup' in results:
            diagnostic_model.set_startup_results(results['startup'])
        if 'drivers' in results:
            diagnostic_model.set_driver_results(results['drivers'])
        if 'security' in results:
            diagnostic_model.set_security_results(results['security'])
        if 'network' in results:
            diagnostic_model.set_network_results(results['network'])
        if 'recommendations' in results:
            diagnostic_model.recommendations = json.dumps(results['recommendations'])
        if 'problems' in results:
            diagnostic_model.notes = json.dumps(results['problems'])
        db.session.add(diagnostic_model)
        db.session.commit()
        results['diagnostic_id'] = diagnostic_model.id
        return jsonify({'success': True, 'results': results, 'diagnostic_id': diagnostic_model.id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def get_status_from_score(score):
    if score >= 90:
        return 'Ótimo'
    elif score >= 70:
        return 'Bom'
    elif score >= 50:
        return 'Regular'
    else:
        return 'Crítico'

def save_diagnostic_results(results):
    # Função auxiliar para salvar resultados (stub)
    pass

def load_diagnostic_results(diagnostic_id):
    # Função auxiliar para carregar resultados (stub)
    pass 