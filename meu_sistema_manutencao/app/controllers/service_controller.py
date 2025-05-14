from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models.service import Service
from app.extensions import db

service_bp = Blueprint('service', __name__)

@service_bp.route('/services', methods=['GET'])
@login_required
def list_services():
    """
    Listar todos os serviços
    """
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso não autorizado'}), 403
    
    services = Service.get_system_services()
    return jsonify([service.to_dict() for service in services]), 200

@service_bp.route('/services/<int:service_id>/status', methods=['GET'])
@login_required
def get_service_status(service_id):
    """
    Obter status de um serviço específico
    """
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso não autorizado'}), 403
    
    service = Service.query.get_or_404(service_id)
    service.update_status()
    return jsonify(service.to_dict()), 200

@service_bp.route('/services/<int:service_id>/start', methods=['POST'])
@login_required
def start_service(service_id):
    """
    Iniciar um serviço
    """
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso não autorizado'}), 403
    
    service = Service.query.get_or_404(service_id)
    try:
        service.start()
        return jsonify({
            'message': f'Serviço {service.name} iniciado com sucesso',
            'service': service.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'error': f'Erro ao iniciar serviço: {str(e)}',
            'service': service.to_dict()
        }), 500

@service_bp.route('/services/<int:service_id>/stop', methods=['POST'])
@login_required
def stop_service(service_id):
    """
    Parar um serviço
    """
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso não autorizado'}), 403
    
    service = Service.query.get_or_404(service_id)
    try:
        service.stop()
        return jsonify({
            'message': f'Serviço {service.name} parado com sucesso',
            'service': service.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'error': f'Erro ao parar serviço: {str(e)}',
            'service': service.to_dict()
        }), 500
