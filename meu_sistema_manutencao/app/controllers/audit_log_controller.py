from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models.audit_log import AuditLog, AuditLogAction
from app.extensions import db

audit_log_bp = Blueprint('audit_log', __name__)

@audit_log_bp.route('/audit-logs', methods=['GET'])
@login_required
def get_audit_logs():
    """
    Obter logs de auditoria com suporte a filtros
    """
    # Verificar se o usuário é admin
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso não autorizado'}), 403
    
    # Parâmetros de filtro
    user_id = request.args.get('user_id', type=int)
    days = request.args.get('days', default=30, type=int)
    action = request.args.get('action')
    
    # Converter ação para enum, se fornecida
    if action:
        try:
            action = AuditLogAction(action)
        except ValueError:
            return jsonify({'error': 'Ação de auditoria inválida'}), 400

    # Obter logs de auditoria
    logs = AuditLog.get_user_activity(
        user_id=user_id, 
        days=days, 
        action=action
    )

    return jsonify([log.to_dict() for log in logs]), 200

@audit_log_bp.route('/audit-logs/export', methods=['GET'])
@login_required
def export_audit_logs():
    """
    Exportar logs de auditoria em CSV
    """
    # Verificar se o usuário é admin
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso não autorizado'}), 403
    
    # Parâmetros de filtro
    user_id = request.args.get('user_id', type=int)
    days = request.args.get('days', default=30, type=int)
    action = request.args.get('action')
    
    # Converter ação para enum, se fornecida
    if action:
        try:
            action = AuditLogAction(action)
        except ValueError:
            return jsonify({'error': 'Ação de auditoria inválida'}), 400

    # Obter logs de auditoria
    logs = AuditLog.get_user_activity(
        user_id=user_id, 
        days=days, 
        action=action
    )

    # Gerar CSV
    import csv
    from io import StringIO
    from flask import make_response

    output = StringIO()
    writer = csv.writer(output)
    
    # Cabeçalho
    writer.writerow([
        'ID', 'Usuário', 'Ação', 'Tipo de Recurso', 
        'ID do Recurso', 'Endereço IP', 'Timestamp'
    ])

    # Dados
    for log in logs:
        writer.writerow([
            log.id, 
            log.username, 
            log.action.value, 
            log.resource_type,
            log.resource_id,
            log.ip_address,
            log.timestamp.isoformat()
        ])

    # Preparar resposta
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=audit_logs_{days}d.csv'
    response.headers['Content-type'] = 'text/csv'
    
    return response
