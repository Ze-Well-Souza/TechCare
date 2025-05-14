from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models.role import PermissionType
from app.models.service_status import ServiceStatus
from app.services.service_monitoring_service import ServiceMonitoringService
import logging

service_monitoring_bp = Blueprint('service_monitoring', __name__)

@service_monitoring_bp.route('/status', methods=['GET'])
@login_required
def get_service_status():
    """
    Endpoint para obter status de serviços
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.SYSTEM_READ):
        return jsonify({'error': 'Sem permissão para visualizar status de serviços'}), 403

    # Obter parâmetros da requisição
    service_name = request.args.get('service_name')
    
    try:
        # Obter status de serviços
        if service_name:
            services = ServiceStatus.get_service_status(service_name)
        else:
            services = ServiceStatus.get_service_status()
        
        # Converter para JSON
        services_data = [{
            'id': service.id,
            'service_name': service.service_name,
            'status': service.status.name,
            'description': service.description,
            'health_check_timestamp': service.health_check_timestamp.isoformat(),
            'cpu_usage': service.cpu_usage,
            'memory_usage': service.memory_usage,
            'response_time': service.response_time,
            'error_details': service.error_details
        } for service in services]
        
        return jsonify(services_data), 200
    
    except Exception as e:
        logging.error(f"Erro ao obter status de serviços: {e}")
        return jsonify({
            'error': 'Erro ao obter status de serviços',
            'details': str(e)
        }), 500

@service_monitoring_bp.route('/health-summary', methods=['GET'])
@login_required
def get_system_health_summary():
    """
    Endpoint para obter resumo de saúde do sistema
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.SYSTEM_READ):
        return jsonify({'error': 'Sem permissão para visualizar resumo de saúde'}), 403
    
    try:
        # Obter resumo de saúde
        health_summary = ServiceStatus.get_system_health_summary()
        
        # Adicionar uso de recursos do sistema
        system_resources = ServiceMonitoringService.get_system_resource_usage()
        
        if system_resources:
            health_summary['system_resources'] = system_resources
        
        return jsonify(health_summary), 200
    
    except Exception as e:
        logging.error(f"Erro ao obter resumo de saúde do sistema: {e}")
        return jsonify({
            'error': 'Erro ao obter resumo de saúde do sistema',
            'details': str(e)
        }), 500

@service_monitoring_bp.route('/check', methods=['POST'])
@login_required
def manual_service_check():
    """
    Endpoint para realizar verificação manual de serviços
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.SYSTEM_CONFIG):
        return jsonify({'error': 'Sem permissão para realizar verificação de serviços'}), 403
    
    try:
        # Realizar verificação de serviços
        ServiceMonitoringService.check_system_services()
        
        return jsonify({
            'message': 'Verificação de serviços concluída',
            'status': 'success'
        }), 200
    
    except Exception as e:
        logging.error(f"Erro ao realizar verificação de serviços: {e}")
        return jsonify({
            'error': 'Erro ao realizar verificação de serviços',
            'details': str(e)
        }), 500
