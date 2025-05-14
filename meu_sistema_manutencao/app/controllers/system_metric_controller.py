from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models.system_metric import SystemMetric
from app.extensions import db
from datetime import datetime, timedelta

system_metric_bp = Blueprint('system_metric', __name__)

@system_metric_bp.route('/metrics/collect', methods=['POST'])
@login_required
def collect_metrics():
    """
    Coletar métricas do sistema
    """
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso não autorizado'}), 403
    
    try:
        metric = SystemMetric.collect_metrics()
        return jsonify(metric.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@system_metric_bp.route('/metrics/recent', methods=['GET'])
@login_required
def get_recent_metrics():
    """
    Obter métricas recentes
    """
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso não autorizado'}), 403
    
    # Parâmetros opcionais
    hours = request.args.get('hours', default=24, type=int)
    limit = request.args.get('limit', default=50, type=int)

    # Calcular tempo de início
    start_time = datetime.utcnow() - timedelta(hours=hours)

    # Buscar métricas
    metrics = SystemMetric.query.filter(
        SystemMetric.timestamp >= start_time
    ).order_by(
        SystemMetric.timestamp.desc()
    ).limit(limit).all()

    return jsonify([metric.to_dict() for metric in metrics]), 200

@system_metric_bp.route('/metrics/summary', methods=['GET'])
@login_required
def get_performance_summary():
    """
    Obter resumo de performance do sistema
    """
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso não autorizado'}), 403
    
    # Parâmetros opcionais
    hours = request.args.get('hours', default=24, type=int)

    try:
        summary = SystemMetric.get_performance_summary(hours)
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@system_metric_bp.route('/metrics/export', methods=['GET'])
@login_required
def export_metrics():
    """
    Exportar métricas em CSV
    """
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso não autorizado'}), 403
    
    # Parâmetros opcionais
    hours = request.args.get('hours', default=24, type=int)
    start_time = datetime.utcnow() - timedelta(hours=hours)

    # Buscar métricas
    metrics = SystemMetric.query.filter(
        SystemMetric.timestamp >= start_time
    ).order_by(
        SystemMetric.timestamp.desc()
    ).all()

    # Gerar CSV
    import csv
    from io import StringIO
    from flask import make_response

    output = StringIO()
    writer = csv.writer(output)
    
    # Cabeçalho
    writer.writerow([
        'Timestamp', 'CPU Usage (%)', 'CPU Cores', 
        'Memory Total', 'Memory Used', 'Memory (%)',
        'Disk Total', 'Disk Used', 'Disk (%)',
        'Network Bytes Sent', 'Network Bytes Received'
    ])

    # Dados
    for metric in metrics:
        writer.writerow([
            metric.timestamp.isoformat(),
            metric.cpu_usage,
            metric.cpu_cores,
            metric.memory_total,
            metric.memory_used,
            metric.memory_percent,
            metric.disk_total,
            metric.disk_used,
            metric.disk_percent,
            metric.network_bytes_sent,
            metric.network_bytes_recv
        ])

    # Preparar resposta
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=system_metrics_{hours}h.csv'
    response.headers['Content-type'] = 'text/csv'
    
    return response
