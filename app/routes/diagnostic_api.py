from flask import request, jsonify
from flask_login import login_required, current_user
from app.services.diagnostic_service import DiagnosticService
from app.services.service_factory import ServiceFactory
from .diagnostic import diagnostic
import copy
import logging

logger = logging.getLogger(__name__)

def _fix_severity_issues(results):
    """
    Corrige problemas com o campo 'severity' nos resultados do diagnóstico
    """
    try:
        # Cria uma cópia dos resultados para evitar alteração do original
        fixed_results = copy.deepcopy(results)
        
        # Corrige issues na seção de memória
        if 'memory' in fixed_results and isinstance(fixed_results['memory'], dict):
            if 'issues' in fixed_results['memory'] and isinstance(fixed_results['memory']['issues'], list):
                for issue in fixed_results['memory']['issues']:
                    if isinstance(issue, dict) and 'severity' not in issue:
                        issue['severity'] = 'high'  # Valor padrão para severity
        
        # Corrige todos os problemas na lista principal
        if 'problems' in fixed_results and isinstance(fixed_results['problems'], list):
            for problem in fixed_results['problems']:
                if isinstance(problem, dict) and 'severity' not in problem:
                    # Usa o campo 'impact' como severity se estiver disponível
                    if 'impact' in problem:
                        problem['severity'] = problem['impact']
                    else:
                        problem['severity'] = 'high'  # Valor padrão para severity
        
        return fixed_results
    except Exception as e:
        logger.error(f"Erro ao corrigir severity: {str(e)}")
        return results  # Retorna o original em caso de erro

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
        
        # Aplica correção para o problema de severity
        fixed_data = _fix_severity_issues(diagnostic_data)
        
        return jsonify({'success': True, 'diagnostic': fixed_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@diagnostic.route('/api/diagnostic/run', methods=['POST'])
@login_required
def api_run_diagnostic():
    try:
        service = ServiceFactory.get_service(DiagnosticService)
        results = service.run_diagnostics(user_id=str(current_user.id))
        
        # Aplica correção para o problema de severity
        fixed_results = _fix_severity_issues(results)
        
        return jsonify({'success': True, 'results': fixed_results})
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
        
        # Aplica correção para o problema de severity
        fixed_data = _fix_severity_issues(diagnostic_data)
        
        return jsonify({'success': True, 'diagnostic': fixed_data})
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
        
        # Aplica correção para o problema de severity
        fixed_info = _fix_severity_issues(system_info)
        
        return jsonify({'success': True, 'system_info': fixed_info})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500 