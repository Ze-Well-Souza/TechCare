from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models.service import Service
from app.models.service_log import ServiceLog
from app.extensions import db

service_log_bp = Blueprint('service_log', __name__)

@service_log_bp.route('/services/<int:service_id>/logs', methods=['GET'])
@login_required
def get_service_logs(service_id):
    """
    Obter logs de um serviço específico
    """
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso não autorizado'}), 403
    
    # Parâmetros de filtro opcionais
    limit = request.args.get('limit', default=50, type=int)
    log_level = request.args.get('log_level')

    # Verificar se o serviço existe
    service = Service.query.get_or_404(service_id)

    # Obter logs
    logs = ServiceLog.get_service_logs(
        service_id=service_id, 
        limit=limit, 
        log_level=log_level
    )

    return jsonify([log.to_dict() for log in logs]), 200

@service_log_bp.route('/services/logs', methods=['GET'])
@login_required
def get_all_service_logs():
    """
    Obter logs de todos os serviços
    """
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso não autorizado'}), 403
    
    # Parâmetros de filtro opcionais
    limit = request.args.get('limit', default=100, type=int)
    log_level = request.args.get('log_level')
    service_id = request.args.get('service_id', type=int)

    # Construir query base
    query = ServiceLog.query

    # Filtros
    if service_id:
        query = query.filter_by(service_id=service_id)
    
    if log_level:
        query = query.filter_by(log_level=log_level)

    # Ordenar e limitar
    logs = query.order_by(ServiceLog.timestamp.desc()).limit(limit).all()

    return jsonify([log.to_dict() for log in logs]), 200

@service_log_bp.route('/services/<int:service_id>/logs/export', methods=['GET'])
@login_required
def export_service_logs(service_id):
    """
    Exportar logs de um serviço em formato CSV
    """
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso não autorizado'}), 403
    
    # Verificar se o serviço existe
    service = Service.query.get_or_404(service_id)

    # Obter logs
    logs = ServiceLog.get_service_logs(service_id=service_id, limit=1000)

    # Gerar CSV
    import csv
    from io import StringIO

    output = StringIO()
    writer = csv.writer(output)
    
    # Cabeçalho
    writer.writerow([
        'ID', 'Timestamp', 'Log Level', 'Mensagem', 
        'Metadados'
    ])

    # Dados
    for log in logs:
        writer.writerow([
            log.id, 
            log.timestamp.isoformat(), 
            log.log_level, 
            log.message, 
            str(log.metadata)
        ])

    # Preparar resposta
    from flask import make_response
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=service_{service_id}_logs.csv'
    response.headers['Content-type'] = 'text/csv'
    
    return response
