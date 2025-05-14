from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models.notification import Notification, NotificationLevel
from app.extensions import db

notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    """
    Obter notificações do usuário
    """
    # Parâmetros de filtro
    unread_only = request.args.get('unread', type=bool, default=True)
    level = request.args.get('level')
    
    # Converter level para enum, se fornecido
    if level:
        try:
            level = NotificationLevel(level)
        except ValueError:
            return jsonify({'error': 'Nível de notificação inválido'}), 400

    # Buscar notificações
    if unread_only:
        notifications = Notification.get_unread_notifications(
            user_id=current_user.id, 
            level=level
        )
    else:
        query = Notification.query.filter_by(user_id=current_user.id)
        if level:
            query = query.filter_by(level=level)
        notifications = query.order_by(Notification.created_at.desc()).all()

    return jsonify([notification.to_dict() for notification in notifications]), 200

@notification_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """
    Marcar notificação específica como lida
    """
    notification = Notification.query.get_or_404(notification_id)
    
    # Verificar se a notificação pertence ao usuário atual
    if notification.user_id != current_user.id:
        return jsonify({'error': 'Acesso não autorizado'}), 403
    
    notification.mark_as_read()
    return jsonify(notification.to_dict()), 200

@notification_bp.route('/notifications/read_all', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """
    Marcar todas as notificações do usuário como lidas
    """
    unread_notifications = Notification.get_unread_notifications(user_id=current_user.id)
    
    for notification in unread_notifications:
        notification.mark_as_read()
    
    return jsonify({
        'message': f'{len(unread_notifications)} notificações marcadas como lidas'
    }), 200

@notification_bp.route('/notifications/system', methods=['POST'])
@login_required
def create_system_notification():
    """
    Criar notificação de sistema (apenas para administradores)
    """
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso não autorizado'}), 403
    
    data = request.get_json()
    
    # Validar dados de entrada
    if not data or 'title' not in data or 'message' not in data:
        return jsonify({'error': 'Título e mensagem são obrigatórios'}), 400
    
    # Nível de notificação
    level = data.get('level', NotificationLevel.INFO.value)
    try:
        level = NotificationLevel(level)
    except ValueError:
        return jsonify({'error': 'Nível de notificação inválido'}), 400
    
    # Criar notificação
    notification = Notification.create_notification(
        title=data['title'],
        message=data['message'],
        level=level
    )
    
    return jsonify(notification.to_dict()), 201
