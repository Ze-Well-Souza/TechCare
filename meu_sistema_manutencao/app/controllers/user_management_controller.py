from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models.role import PermissionType
from app.services.user_management_service import UserManagementService
import logging

user_management_bp = Blueprint('user_management', __name__)

@user_management_bp.route('/users', methods=['POST'])
@login_required
def create_user():
    """
    Endpoint para criar usuário
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.USER_MANAGEMENT):
        return jsonify({'error': 'Sem permissão para gerenciar usuários'}), 403

    # Obter dados da requisição
    data = request.json
    
    if not data or not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({'error': 'Dados de usuário incompletos'}), 400
    
    try:
        # Criar usuário
        result = UserManagementService.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            role_name=data.get('role'),
            admin_user_id=current_user.id
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    
    except Exception as e:
        logging.error(f"Erro ao criar usuário: {e}")
        return jsonify({
            'error': 'Erro ao criar usuário',
            'details': str(e)
        }), 500

@user_management_bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    """
    Endpoint para atualizar usuário
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.USER_MANAGEMENT):
        return jsonify({'error': 'Sem permissão para gerenciar usuários'}), 403

    # Obter dados da requisição
    data = request.json
    
    if not data:
        return jsonify({'error': 'Nenhum dado fornecido para atualização'}), 400
    
    try:
        # Atualizar usuário
        result = UserManagementService.update_user(
            user_id=user_id,
            username=data.get('username'),
            email=data.get('email'),
            role_name=data.get('role'),
            admin_user_id=current_user.id
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    except Exception as e:
        logging.error(f"Erro ao atualizar usuário: {e}")
        return jsonify({
            'error': 'Erro ao atualizar usuário',
            'details': str(e)
        }), 500

@user_management_bp.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    """
    Endpoint para excluir usuário
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.USER_MANAGEMENT):
        return jsonify({'error': 'Sem permissão para gerenciar usuários'}), 403

    try:
        # Excluir usuário
        result = UserManagementService.delete_user(
            user_id=user_id,
            admin_user_id=current_user.id
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
    
    except Exception as e:
        logging.error(f"Erro ao excluir usuário: {e}")
        return jsonify({
            'error': 'Erro ao excluir usuário',
            'details': str(e)
        }), 500

@user_management_bp.route('/users', methods=['GET'])
@login_required
def list_users():
    """
    Endpoint para listar usuários por role
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.USER_READ):
        return jsonify({'error': 'Sem permissão para visualizar usuários'}), 403

    # Obter parâmetros da requisição
    role = request.args.get('role')
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=10)
    
    try:
        # Listar usuários
        result = UserManagementService.get_users_by_role(
            role_name=role,
            page=page,
            per_page=per_page
        )
        
        return jsonify(result), 200
    
    except Exception as e:
        logging.error(f"Erro ao listar usuários: {e}")
        return jsonify({
            'error': 'Erro ao listar usuários',
            'details': str(e)
        }), 500

@user_management_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
def reset_user_password(user_id):
    """
    Endpoint para redefinir senha de usuário
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.USER_MANAGEMENT):
        return jsonify({'error': 'Sem permissão para gerenciar usuários'}), 403

    # Obter dados da requisição
    data = request.json
    
    if not data or 'new_password' not in data:
        return jsonify({'error': 'Nova senha não fornecida'}), 400
    
    try:
        # Redefinir senha
        result = UserManagementService.reset_user_password(
            user_id=user_id,
            new_password=data['new_password'],
            admin_user_id=current_user.id
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    except Exception as e:
        logging.error(f"Erro ao redefinir senha do usuário: {e}")
        return jsonify({
            'error': 'Erro ao redefinir senha',
            'details': str(e)
        }), 500
