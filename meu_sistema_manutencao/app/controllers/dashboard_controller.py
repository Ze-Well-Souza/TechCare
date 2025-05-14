from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models.role import PermissionType
from app.services.dashboard_service import DashboardService
import logging

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/overview', methods=['GET'])
@login_required
def get_system_overview():
    """
    Endpoint para obter visão geral do sistema
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.DASHBOARD_READ):
        return jsonify({'error': 'Sem permissão para visualizar dashboard'}), 403

    # Obter parâmetros da requisição
    days = request.args.get('days', type=int, default=7)
    
    try:
        # Obter visão geral do sistema
        overview = DashboardService.get_system_overview(days)
        
        if overview is None:
            return jsonify({
                'error': 'Erro ao obter visão geral do sistema'
            }), 500
        
        return jsonify(overview), 200
    
    except Exception as e:
        logging.error(f"Erro ao obter visão geral do sistema: {e}")
        return jsonify({
            'error': 'Erro ao obter visão geral do sistema',
            'details': str(e)
        }), 500

@dashboard_bp.route('/performance-chart', methods=['GET'])
@login_required
def get_performance_chart():
    """
    Endpoint para obter dados de gráfico de performance
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.DASHBOARD_READ):
        return jsonify({'error': 'Sem permissão para visualizar dashboard'}), 403

    # Obter parâmetros da requisição
    metric = request.args.get('metric', 'cpu_usage')
    days = request.args.get('days', type=int, default=7)
    
    try:
        # Obter dados históricos de performance
        performance_data = DashboardService.get_performance_history(
            metric=metric, 
            days=days
        )
        
        return jsonify(performance_data), 200
    
    except Exception as e:
        logging.error(f"Erro ao obter dados de performance: {e}")
        return jsonify({
            'error': 'Erro ao obter dados de performance',
            'details': str(e)
        }), 500

@dashboard_bp.route('/top-issues', methods=['GET'])
@login_required
def get_top_issues():
    """
    Endpoint para obter principais problemas e alertas
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.DASHBOARD_READ):
        return jsonify({'error': 'Sem permissão para visualizar dashboard'}), 403

    # Obter parâmetros da requisição
    days = request.args.get('days', type=int, default=7)
    
    try:
        # Obter lista de problemas e alertas
        top_issues = DashboardService.get_top_system_issues(days)
        
        return jsonify(top_issues), 200
    
    except Exception as e:
        logging.error(f"Erro ao obter problemas do sistema: {e}")
        return jsonify({
            'error': 'Erro ao obter problemas do sistema',
            'details': str(e)
        }), 500
