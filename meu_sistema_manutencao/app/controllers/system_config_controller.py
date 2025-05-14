from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models.role import PermissionType
from app.services.system_config_service import SystemConfigService
import logging

system_config_bp = Blueprint('system_config', __name__)

@system_config_bp.route('/', methods=['GET'])
@login_required
def get_all_configs():
    """
    Endpoint para obter todas as configurações
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.SYSTEM_READ):
        return jsonify({'error': 'Sem permissão para visualizar configurações'}), 403

    # Obter parâmetros da requisição
    include_sensitive = request.args.get('include_sensitive', type=bool, default=False)
    
    try:
        # Obter configurações
        configs = SystemConfigService.get_all_configs(include_sensitive)
        
        return jsonify(configs), 200
    
    except Exception as e:
        logging.error(f"Erro ao obter configurações: {e}")
        return jsonify({
            'error': 'Erro ao obter configurações',
            'details': str(e)
        }), 500

@system_config_bp.route('/<string:config_key>', methods=['GET'])
@login_required
def get_config(config_key):
    """
    Endpoint para obter uma configuração específica
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.SYSTEM_READ):
        return jsonify({'error': 'Sem permissão para visualizar configurações'}), 403

    try:
        # Obter configuração
        config_value = SystemConfigService.get_config(config_key)
        
        if config_value is None:
            return jsonify({
                'error': f'Configuração {config_key} não encontrada'
            }), 404
        
        return jsonify({
            'config_key': config_key,
            'config_value': config_value
        }), 200
    
    except Exception as e:
        logging.error(f"Erro ao obter configuração {config_key}: {e}")
        return jsonify({
            'error': f'Erro ao obter configuração {config_key}',
            'details': str(e)
        }), 500

@system_config_bp.route('/', methods=['POST'])
@login_required
def create_config():
    """
    Endpoint para criar/atualizar configuração
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.SYSTEM_CONFIG):
        return jsonify({'error': 'Sem permissão para configurar o sistema'}), 403

    # Obter dados da requisição
    data = request.json
    
    if not data or 'config_key' not in data or 'config_value' not in data:
        return jsonify({'error': 'Dados de configuração inválidos'}), 400
    
    try:
        # Atualizar configuração
        result = SystemConfigService.update_config(
            config_key=data['config_key'],
            config_value=data['config_value'],
            description=data.get('description'),
            is_sensitive=data.get('is_sensitive', False),
            user_id=current_user.id
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    except Exception as e:
        logging.error(f"Erro ao criar/atualizar configuração: {e}")
        return jsonify({
            'error': 'Erro ao criar/atualizar configuração',
            'details': str(e)
        }), 500

@system_config_bp.route('/<string:config_key>', methods=['DELETE'])
@login_required
def delete_config(config_key):
    """
    Endpoint para excluir configuração
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.SYSTEM_CONFIG):
        return jsonify({'error': 'Sem permissão para configurar o sistema'}), 403

    try:
        # Excluir configuração
        result = SystemConfigService.delete_config(
            config_key=config_key,
            user_id=current_user.id
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
    
    except Exception as e:
        logging.error(f"Erro ao excluir configuração {config_key}: {e}")
        return jsonify({
            'error': f'Erro ao excluir configuração {config_key}',
            'details': str(e)
        }), 500

@system_config_bp.route('/load-defaults', methods=['POST'])
@login_required
def load_default_configs():
    """
    Endpoint para carregar configurações padrão
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.SYSTEM_CONFIG):
        return jsonify({'error': 'Sem permissão para configurar o sistema'}), 403

    try:
        # Carregar configurações padrão
        SystemConfigService.load_default_configs()
        
        return jsonify({
            'message': 'Configurações padrão carregadas com sucesso',
            'status': 'success'
        }), 200
    
    except Exception as e:
        logging.error(f"Erro ao carregar configurações padrão: {e}")
        return jsonify({
            'error': 'Erro ao carregar configurações padrão',
            'details': str(e)
        }), 500
