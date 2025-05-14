from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.user_role_service import UserRoleService
from app.models.role import PermissionType
import logging

user_role_bp = Blueprint('user_role', __name__)

@user_role_bp.route('/users', methods=['POST'])
@login_required
def create_user():
    """
    Endpoint para criação de usuário
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.USER_CREATE):
        return jsonify({'error': 'Sem permissão para criar usuários'}), 403

    # Obter dados da requisição
    data = request.get_json()
    
    try:
        # Validar dados obrigatórios
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role_name = data.get('role', 'Visualizador')

        if not all([username, email, password]):
            return jsonify({'error': 'Dados incompletos'}), 400

        # Criar usuário
        user = UserRoleService.create_user(
            username=username, 
            email=email, 
            password=password,
            role_name=role_name
        )

        return jsonify({
            'message': 'Usuário criado com sucesso',
            'user_id': user.id,
            'username': user.username
        }), 201

    except Exception as e:
        logging.error(f"Erro ao criar usuário: {e}")
        return jsonify({
            'error': 'Erro ao criar usuário',
            'details': str(e)
        }), 500

@user_role_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@login_required
def update_user_role(user_id):
    """
    Endpoint para atualização de role de usuário
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.USER_UPDATE):
        return jsonify({'error': 'Sem permissão para atualizar usuários'}), 403

    # Obter dados da requisição
    data = request.get_json()
    
    try:
        # Validar dados obrigatórios
        new_role_name = data.get('role')
        if not new_role_name:
            return jsonify({'error': 'Role não especificada'}), 400

        # Atualizar role
        user = UserRoleService.update_user_role(
            user_id=user_id, 
            new_role_name=new_role_name
        )

        return jsonify({
            'message': 'Role do usuário atualizada com sucesso',
            'user_id': user.id,
            'new_role': user.role.name
        }), 200

    except Exception as e:
        logging.error(f"Erro ao atualizar role do usuário: {e}")
        return jsonify({
            'error': 'Erro ao atualizar role do usuário',
            'details': str(e)
        }), 500

@user_role_bp.route('/users/by-role/<string:role_name>', methods=['GET'])
@login_required
def get_users_by_role(role_name):
    """
    Endpoint para obter usuários por role
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.USER_READ):
        return jsonify({'error': 'Sem permissão para listar usuários'}), 403

    try:
        # Obter usuários
        users = UserRoleService.get_users_by_role(role_name)
        
        # Converter para JSON
        users_data = [{
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role.name
        } for user in users]

        return jsonify({
            'users': users_data,
            'total': len(users_data)
        }), 200

    except Exception as e:
        logging.error(f"Erro ao buscar usuários por role: {e}")
        return jsonify({
            'error': 'Erro ao buscar usuários',
            'details': str(e)
        }), 500

@user_role_bp.route('/roles/<string:role_name>/permissions', methods=['POST'])
@login_required
def add_role_permission(role_name):
    """
    Endpoint para adicionar permissão a uma role
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.SYSTEM_CONFIG):
        return jsonify({'error': 'Sem permissão para configurar roles'}), 403

    # Obter dados da requisição
    data = request.get_json()
    
    try:
        # Validar dados obrigatórios
        permission_name = data.get('permission')
        if not permission_name:
            return jsonify({'error': 'Permissão não especificada'}), 400

        # Converter nome da permissão para enum
        try:
            permission = PermissionType[permission_name]
        except KeyError:
            return jsonify({'error': 'Permissão inválida'}), 400

        # Adicionar permissão
        UserRoleService.add_permission_to_role(
            role_name=role_name, 
            permission=permission
        )

        return jsonify({
            'message': 'Permissão adicionada com sucesso',
            'role': role_name,
            'permission': permission_name
        }), 200

    except Exception as e:
        logging.error(f"Erro ao adicionar permissão à role: {e}")
        return jsonify({
            'error': 'Erro ao adicionar permissão',
            'details': str(e)
        }), 500

@user_role_bp.route('/roles/<string:role_name>/permissions', methods=['DELETE'])
@login_required
def remove_role_permission(role_name):
    """
    Endpoint para remover permissão de uma role
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.SYSTEM_CONFIG):
        return jsonify({'error': 'Sem permissão para configurar roles'}), 403

    # Obter dados da requisição
    data = request.get_json()
    
    try:
        # Validar dados obrigatórios
        permission_name = data.get('permission')
        if not permission_name:
            return jsonify({'error': 'Permissão não especificada'}), 400

        # Converter nome da permissão para enum
        try:
            permission = PermissionType[permission_name]
        except KeyError:
            return jsonify({'error': 'Permissão inválida'}), 400

        # Remover permissão
        UserRoleService.remove_permission_from_role(
            role_name=role_name, 
            permission=permission
        )

        return jsonify({
            'message': 'Permissão removida com sucesso',
            'role': role_name,
            'permission': permission_name
        }), 200

    except Exception as e:
        logging.error(f"Erro ao remover permissão da role: {e}")
        return jsonify({
            'error': 'Erro ao remover permissão',
            'details': str(e)
        }), 500
