from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models.role import PermissionType
from app.services.service_management_service import ServiceManagementService
import logging

service_management_bp = Blueprint('service_management', __name__)

@service_management_bp.route('/stop', methods=['POST'])
@login_required
def stop_service():
    """
    Endpoint para parar um serviço
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.SYSTEM_CONFIG):
        return jsonify({'error': 'Sem permissão para parar serviços'}), 403

    # Obter parâmetros da requisição
    service_name = request.json.get('service_name')
    
    if not service_name:
        return jsonify({'error': 'Nome do serviço não fornecido'}), 400
    
    try:
        # Parar serviço
        result = ServiceManagementService.stop_service(
            service_name=service_name, 
            user_id=current_user.id
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
    
    except Exception as e:
        logging.error(f"Erro ao parar serviço: {e}")
        return jsonify({
            'error': 'Erro ao parar serviço',
            'details': str(e)
        }), 500

@service_management_bp.route('/start', methods=['POST'])
@login_required
def start_service():
    """
    Endpoint para iniciar um serviço
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.SYSTEM_CONFIG):
        return jsonify({'error': 'Sem permissão para iniciar serviços'}), 403

    # Obter parâmetros da requisição
    service_name = request.json.get('service_name')
    
    if not service_name:
        return jsonify({'error': 'Nome do serviço não fornecido'}), 400
    
    try:
        # Iniciar serviço
        result = ServiceManagementService.start_service(
            service_name=service_name, 
            user_id=current_user.id
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
    
    except Exception as e:
        logging.error(f"Erro ao iniciar serviço: {e}")
        return jsonify({
            'error': 'Erro ao iniciar serviço',
            'details': str(e)
        }), 500

@service_management_bp.route('/restart', methods=['POST'])
@login_required
def restart_service():
    """
    Endpoint para reiniciar um serviço
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.SYSTEM_CONFIG):
        return jsonify({'error': 'Sem permissão para reiniciar serviços'}), 403

    # Obter parâmetros da requisição
    service_name = request.json.get('service_name')
    
    if not service_name:
        return jsonify({'error': 'Nome do serviço não fornecido'}), 400
    
    try:
        # Reiniciar serviço
        result = ServiceManagementService.restart_service(
            service_name=service_name, 
            user_id=current_user.id
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
    
    except Exception as e:
        logging.error(f"Erro ao reiniciar serviço: {e}")
        return jsonify({
            'error': 'Erro ao reiniciar serviço',
            'details': str(e)
        }), 500
