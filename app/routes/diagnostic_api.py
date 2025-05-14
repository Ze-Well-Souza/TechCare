from flask import request, jsonify
from flask_login import login_required, current_user
from app.services.diagnostic_service import DiagnosticService
from app.services.service_factory import ServiceFactory
from .diagnostic import diagnostic

@diagnostic.route('/api/repository/history')
@login_required
def api_repository_history():
    try:
        service = ServiceFactory.get_service(DiagnosticService)
        history = service.get_diagnostic_history(user_id=str(current_user.id))
        return jsonify({'success': True, 'history': history})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@diagnostic.route('/api/repository/diagnostic/<diagnostic_id>')
@login_required
def api_repository_diagnostic(diagnostic_id):
    try:
        service = ServiceFactory.get_service(DiagnosticService)
        diagnostic_data = service.get_diagnostic_by_id(diagnostic_id, user_id=str(current_user.id))
        if not diagnostic_data:
            return jsonify({'success': False, 'error': 'Diagnóstico não encontrado'}), 404
        return jsonify({'success': True, 'diagnostic': diagnostic_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@diagnostic.route('/api/diagnostic/run', methods=['POST'])
@login_required
def api_run_diagnostic():
    try:
        service = ServiceFactory.get_service(DiagnosticService)
        results = service.run_diagnostics(user_id=str(current_user.id))
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@diagnostic.route('/api/diagnostic/history', methods=['GET'])
@login_required
def api_diagnostic_history():
    try:
        service = ServiceFactory.get_service(DiagnosticService)
        history = service.get_diagnostic_history(user_id=str(current_user.id))
        return jsonify({'success': True, 'history': history})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@diagnostic.route('/api/diagnostic/<diagnostic_id>', methods=['GET'])
@login_required
def api_get_diagnostic(diagnostic_id):
    try:
        service = ServiceFactory.get_service(DiagnosticService)
        diagnostic_data = service.get_diagnostic_by_id(diagnostic_id, user_id=str(current_user.id))
        if not diagnostic_data:
            return jsonify({'success': False, 'error': 'Diagnóstico não encontrado'}), 404
        return jsonify({'success': True, 'diagnostic': diagnostic_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@diagnostic.route('/api/diagnostic/metrics', methods=['GET'])
@login_required
def api_system_metrics():
    try:
        service = ServiceFactory.get_service(DiagnosticService)
        metrics = service.get_system_metrics(user_id=str(current_user.id))
        return jsonify({'success': True, 'metrics': metrics})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@diagnostic.route('/api/admin/diagnostics', methods=['GET'])
@login_required
def api_admin_diagnostics():
    if not current_user.is_admin():
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    try:
        service = ServiceFactory.get_service(DiagnosticService)
        diagnostics = service.get_all_diagnostics()
        return jsonify({'success': True, 'diagnostics': diagnostics})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@diagnostic.route('/api/diagnostic/system-status', methods=['GET'])
@login_required
def system_status():
    """Retorna o status atual do sistema para atualização via AJAX"""
    try:
        service = ServiceFactory.get_service(DiagnosticService)
        system_info = service.get_system_summary()
        return jsonify({'success': True, 'system_info': system_info})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500 