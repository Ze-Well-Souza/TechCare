from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.services.audit_log_anomaly_notification_service import AuditLogAnomalyNotificationService

audit_log_anomaly_notification_bp = Blueprint('audit_log_anomaly_notification', __name__)

@audit_log_anomaly_notification_bp.route('/check', methods=['POST'])
@login_required
def check_anomalies():
    """
    Endpoint para verificar e notificar anomalias
    """
    # Verificar se o usuário é admin
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso não autorizado'}), 403

    # Obter parâmetros da requisição
    days = request.json.get('days', 1)

    try:
        # Verificar anomalias
        anomalies = AuditLogAnomalyNotificationService.check_and_notify_anomalies(days)
        
        return jsonify({
            'message': 'Verificação de anomalias concluída',
            'anomalies': anomalies
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Erro na verificação de anomalias',
            'details': str(e)
        }), 500

@audit_log_anomaly_notification_bp.route('/recent', methods=['GET'])
@login_required
def get_recent_anomalies():
    """
    Endpoint para obter notificações de anomalias recentes
    """
    # Verificar se o usuário é admin
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso não autorizado'}), 403

    # Obter parâmetros da requisição
    days = request.args.get('days', default=7, type=int)

    try:
        # Obter notificações recentes
        notifications = AuditLogAnomalyNotificationService.get_recent_anomaly_notifications(days)
        
        # Converter notificações para formato JSON
        notifications_data = [{
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'level': n.level.value,
            'timestamp': n.timestamp.isoformat()
        } for n in notifications]
        
        return jsonify({
            'notifications': notifications_data,
            'total': len(notifications)
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Erro ao obter notificações de anomalias',
            'details': str(e)
        }), 500
