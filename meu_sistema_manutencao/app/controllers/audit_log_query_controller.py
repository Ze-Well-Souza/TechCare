from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app.services.audit_log_query_service import AuditLogQueryService

audit_log_query_bp = Blueprint('audit_log_query', __name__)

@audit_log_query_bp.route('/advanced-search', methods=['POST'])
@login_required
def advanced_search():
    """
    Endpoint para busca avançada de logs de auditoria
    """
    # Verificar se o usuário é admin
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso não autorizado'}), 403

    # Parâmetros de busca
    data = request.get_json()

    # Converter datas
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    if start_date:
        start_date = datetime.fromisoformat(start_date)
    if end_date:
        end_date = datetime.fromisoformat(end_date)

    # Parâmetros opcionais
    user_ids = data.get('user_ids', [])
    actions = data.get('actions', [])
    resource_types = data.get('resource_types', [])
    ip_addresses = data.get('ip_addresses', [])
    
    # Paginação
    page = data.get('page', 1)
    per_page = data.get('per_page', 50)

    try:
        # Realizar busca avançada
        logs, total_logs = AuditLogQueryService.advanced_search(
            start_date=start_date,
            end_date=end_date,
            user_ids=user_ids,
            actions=actions,
            resource_types=resource_types,
            ip_addresses=ip_addresses,
            page=page,
            per_page=per_page
        )

        # Converter logs para dicionário
        logs_data = [log.to_dict() for log in logs]

        return jsonify({
            'logs': logs_data,
            'total_logs': total_logs,
            'page': page,
            'per_page': per_page
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Erro na busca avançada de logs',
            'details': str(e)
        }), 500

@audit_log_query_bp.route('/anomaly-report', methods=['GET'])
@login_required
def anomaly_report():
    """
    Endpoint para gerar relatório de anomalias
    """
    # Verificar se o usuário é admin
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso não autorizado'}), 403

    # Parâmetro opcional de dias
    days = request.args.get('days', default=30, type=int)

    try:
        # Gerar relatório de anomalias
        anomalies = AuditLogQueryService.generate_anomaly_report(days)
        
        return jsonify({
            'anomalies': anomalies,
            'analysis_period_days': days
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Erro ao gerar relatório de anomalias',
            'details': str(e)
        }), 500
