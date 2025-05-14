from flask import Blueprint, request, send_file, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app.services.audit_log_export_service import AuditLogExportService
from io import BytesIO

audit_log_export_bp = Blueprint('audit_log_export', __name__)

@audit_log_export_bp.route('/export', methods=['POST'])
@login_required
def export_audit_logs():
    """
    Endpoint para exportação de logs de auditoria
    """
    # Verificar se o usuário é admin
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso não autorizado'}), 403

    # Obter dados da requisição
    data = request.get_json()

    # Parâmetros de exportação
    export_format = data.get('format', 'csv')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    user_ids = data.get('user_ids', [])
    actions = data.get('actions', [])
    resource_types = data.get('resource_types', [])
    ip_addresses = data.get('ip_addresses', [])

    # Converter datas
    if start_date:
        start_date = datetime.fromisoformat(start_date)
    if end_date:
        end_date = datetime.fromisoformat(end_date)

    try:
        # Exportar logs
        filename, file_content = AuditLogExportService.export_logs(
            export_format=export_format,
            start_date=start_date,
            end_date=end_date,
            user_ids=user_ids,
            actions=actions,
            resource_types=resource_types,
            ip_addresses=ip_addresses
        )

        # Gerar resumo da exportação
        logs_data = AuditLogExportService.export_logs(
            export_format='json',
            start_date=start_date,
            end_date=end_date,
            user_ids=user_ids,
            actions=actions,
            resource_types=resource_types,
            ip_addresses=ip_addresses
        )[1]

        # Converter logs JSON para dicionário
        logs_data = json.loads(logs_data)
        export_summary = AuditLogExportService.generate_export_summary(logs_data)

        # Preparar arquivo para download
        if export_format == 'csv':
            mime_type = 'text/csv'
        elif export_format == 'json':
            mime_type = 'application/json'
        elif export_format == 'xml':
            mime_type = 'application/xml'
        elif export_format == 'xlsx':
            mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        else:
            return jsonify({'error': 'Formato de exportação inválido'}), 400

        # Enviar arquivo
        return send_file(
            BytesIO(file_content.encode() if isinstance(file_content, str) else file_content),
            mimetype=mime_type,
            as_attachment=True,
            download_name=filename,
            attachment_filename=filename
        )

    except Exception as e:
        return jsonify({
            'error': 'Erro na exportação de logs',
            'details': str(e)
        }), 500

@audit_log_export_bp.route('/export-summary', methods=['POST'])
@login_required
def get_export_summary():
    """
    Endpoint para obter resumo da exportação de logs
    """
    # Verificar se o usuário é admin
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso não autorizado'}), 403

    # Obter dados da requisição
    data = request.get_json()

    # Parâmetros de exportação
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    user_ids = data.get('user_ids', [])
    actions = data.get('actions', [])
    resource_types = data.get('resource_types', [])
    ip_addresses = data.get('ip_addresses', [])

    # Converter datas
    if start_date:
        start_date = datetime.fromisoformat(start_date)
    if end_date:
        end_date = datetime.fromisoformat(end_date)

    try:
        # Exportar logs em JSON para gerar resumo
        logs_data = AuditLogExportService.export_logs(
            export_format='json',
            start_date=start_date,
            end_date=end_date,
            user_ids=user_ids,
            actions=actions,
            resource_types=resource_types,
            ip_addresses=ip_addresses
        )[1]

        # Converter logs JSON para dicionário
        logs_data = json.loads(logs_data)
        export_summary = AuditLogExportService.generate_export_summary(logs_data)

        return jsonify({
            'summary': export_summary,
            'total_logs': len(logs_data)
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Erro ao gerar resumo de exportação',
            'details': str(e)
        }), 500
