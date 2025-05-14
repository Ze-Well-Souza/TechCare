from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.user_activity_service import UserActivityService
from app.models.role import PermissionType
from datetime import datetime
import logging

user_activity_bp = Blueprint('user_activity', __name__)

@user_activity_bp.route('/logs', methods=['GET'])
@login_required
def get_user_activities():
    """
    Endpoint para obter logs de atividade do usuário
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.USER_READ):
        return jsonify({'error': 'Sem permissão para visualizar logs'}), 403

    # Obter parâmetros da requisição
    user_id = request.args.get('user_id', type=int, default=current_user.id)
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=50)
    
    try:
        # Converter datas
        start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else None
        
        # Obter logs de atividade
        activities, total = UserActivityLog.get_user_activities(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            page=page,
            per_page=per_page
        )
        
        # Converter para JSON
        activities_data = [{
            'id': activity.id,
            'user_id': activity.user_id,
            'activity_type': activity.activity_type.name,
            'description': activity.description,
            'ip_address': activity.ip_address,
            'timestamp': activity.timestamp.isoformat()
        } for activity in activities]
        
        return jsonify({
            'activities': activities_data,
            'total': total,
            'page': page,
            'per_page': per_page
        }), 200
    
    except Exception as e:
        logging.error(f"Erro ao obter logs de atividade: {e}")
        return jsonify({
            'error': 'Erro ao obter logs de atividade',
            'details': str(e)
        }), 500

@user_activity_bp.route('/summary', methods=['GET'])
@login_required
def get_activity_summary():
    """
    Endpoint para obter resumo de atividades do usuário
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.USER_READ):
        return jsonify({'error': 'Sem permissão para visualizar resumo'}), 403

    # Obter parâmetros da requisição
    user_id = request.args.get('user_id', type=int, default=current_user.id)
    days = request.args.get('days', type=int, default=30)
    
    try:
        # Obter resumo de atividades
        summary = UserActivityService.get_user_activity_summary(
            user_id=user_id,
            days=days
        )
        
        return jsonify({
            'summary': summary
        }), 200
    
    except Exception as e:
        logging.error(f"Erro ao obter resumo de atividades: {e}")
        return jsonify({
            'error': 'Erro ao obter resumo de atividades',
            'details': str(e)
        }), 500

@user_activity_bp.route('/cleanup', methods=['POST'])
@login_required
def cleanup_activity_logs():
    """
    Endpoint para limpar logs de atividade antigos
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.SYSTEM_CONFIG):
        return jsonify({'error': 'Sem permissão para limpar logs'}), 403

    # Obter parâmetros da requisição
    retention_days = request.json.get('retention_days', 90)
    
    try:
        # Limpar logs antigos
        deleted_count = UserActivityService.cleanup_old_activity_logs(
            retention_days=retention_days
        )
        
        return jsonify({
            'message': 'Limpeza de logs concluída',
            'deleted_logs': deleted_count
        }), 200
    
    except Exception as e:
        logging.error(f"Erro ao limpar logs de atividade: {e}")
        return jsonify({
            'error': 'Erro ao limpar logs de atividade',
            'details': str(e)
        }), 500
