from flask import Blueprint, jsonify
from flask_login import login_required
from app.services.audit_log_retention_service import AuditLogRetentionService

audit_log_retention_bp = Blueprint('audit_log_retention', __name__)

@audit_log_retention_bp.route('/retention-summary', methods=['GET'])
@login_required
def get_log_retention_summary():
    """
    Endpoint para obter resumo de retenção de logs de auditoria
    """
    try:
        summary = AuditLogRetentionService.get_log_retention_summary()
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({
            'error': 'Erro ao obter resumo de retenção de logs',
            'details': str(e)
        }), 500

@audit_log_retention_bp.route('/cleanup', methods=['POST'])
@login_required
def trigger_log_cleanup():
    """
    Endpoint para acionar limpeza manual de logs
    """
    try:
        # Executar limpeza de logs
        cleanup_stats = AuditLogRetentionService.clean_expired_logs()
        return jsonify({
            'message': 'Limpeza de logs concluída',
            'stats': cleanup_stats
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Erro ao limpar logs',
            'details': str(e)
        }), 500
