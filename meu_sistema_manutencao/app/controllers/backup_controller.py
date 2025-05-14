from flask import Blueprint, jsonify, request, send_file
from flask_login import login_required, current_user
from app.models.role import PermissionType
from app.services.backup_service import BackupService
import os
import logging

backup_bp = Blueprint('backup', __name__)

@backup_bp.route('/database', methods=['POST'])
@login_required
def create_database_backup():
    """
    Endpoint para criar backup de banco de dados
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.SYSTEM_BACKUP):
        return jsonify({'error': 'Sem permissão para criar backup'}), 403

    # Obter descrição opcional
    description = request.json.get('description') if request.json else None
    
    try:
        # Criar backup
        result = BackupService.create_database_backup(description)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
    
    except Exception as e:
        logging.error(f"Erro ao criar backup de banco de dados: {e}")
        return jsonify({
            'error': 'Erro ao criar backup de banco de dados',
            'details': str(e)
        }), 500

@backup_bp.route('/files', methods=['POST'])
@login_required
def create_file_backup():
    """
    Endpoint para criar backup de arquivos
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.SYSTEM_BACKUP):
        return jsonify({'error': 'Sem permissão para criar backup'}), 403

    # Obter parâmetros da requisição
    data = request.json or {}
    directories = data.get('directories')
    description = data.get('description')
    
    try:
        # Criar backup
        result = BackupService.create_file_backup(
            directories=directories, 
            description=description
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
    
    except Exception as e:
        logging.error(f"Erro ao criar backup de arquivos: {e}")
        return jsonify({
            'error': 'Erro ao criar backup de arquivos',
            'details': str(e)
        }), 500

@backup_bp.route('/restore/database', methods=['POST'])
@login_required
def restore_database_backup():
    """
    Endpoint para restaurar backup de banco de dados
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.SYSTEM_RESTORE):
        return jsonify({'error': 'Sem permissão para restaurar backup'}), 403

    # Obter nome do arquivo de backup
    data = request.json
    if not data or 'backup_file' not in data:
        return jsonify({'error': 'Nome do arquivo de backup não fornecido'}), 400
    
    try:
        # Restaurar backup
        result = BackupService.restore_database_backup(
            backup_filename=data['backup_file'],
            user_id=current_user.id
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
    
    except Exception as e:
        logging.error(f"Erro ao restaurar backup de banco de dados: {e}")
        return jsonify({
            'error': 'Erro ao restaurar backup de banco de dados',
            'details': str(e)
        }), 500

@backup_bp.route('/restore/files', methods=['POST'])
@login_required
def restore_file_backup():
    """
    Endpoint para restaurar backup de arquivos
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.SYSTEM_RESTORE):
        return jsonify({'error': 'Sem permissão para restaurar backup'}), 403

    # Obter nome do arquivo de backup
    data = request.json
    if not data or 'backup_file' not in data:
        return jsonify({'error': 'Nome do arquivo de backup não fornecido'}), 400
    
    try:
        # Restaurar backup
        result = BackupService.restore_file_backup(
            backup_filename=data['backup_file'],
            user_id=current_user.id
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
    
    except Exception as e:
        logging.error(f"Erro ao restaurar backup de arquivos: {e}")
        return jsonify({
            'error': 'Erro ao restaurar backup de arquivos',
            'details': str(e)
        }), 500

@backup_bp.route('/list', methods=['GET'])
@login_required
def list_backups():
    """
    Endpoint para listar backups disponíveis
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.SYSTEM_BACKUP_READ):
        return jsonify({'error': 'Sem permissão para listar backups'}), 403

    # Obter tipo de backup (opcional)
    backup_type = request.args.get('type')
    
    try:
        # Listar backups
        result = BackupService.list_backups(backup_type)
        
        return jsonify(result), 200
    
    except Exception as e:
        logging.error(f"Erro ao listar backups: {e}")
        return jsonify({
            'error': 'Erro ao listar backups',
            'details': str(e)
        }), 500

@backup_bp.route('/download/<string:filename>', methods=['GET'])
@login_required
def download_backup(filename):
    """
    Endpoint para download de backup
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.SYSTEM_BACKUP_READ):
        return jsonify({'error': 'Sem permissão para baixar backup'}), 403

    try:
        # Caminho completo do arquivo de backup
        backup_path = os.path.join(BackupService.BACKUP_BASE_DIR, filename)
        
        # Verificar se arquivo existe
        if not os.path.exists(backup_path):
            return jsonify({'error': 'Arquivo de backup não encontrado'}), 404
        
        # Registrar log de auditoria
        AuditLog.log_activity(
            user_id=current_user.id,
            action_type=AuditLogType.SYSTEM_BACKUP_DOWNLOAD,
            description='Download de backup',
            details={'backup_file': filename}
        )
        
        # Enviar arquivo para download
        return send_file(
            backup_path, 
            as_attachment=True, 
            download_name=filename
        )
    
    except Exception as e:
        logging.error(f"Erro ao baixar backup: {e}")
        return jsonify({
            'error': 'Erro ao baixar backup',
            'details': str(e)
        }), 500

@backup_bp.route('/schedule', methods=['POST'])
@login_required
def schedule_backup():
    """
    Endpoint para configurar backup agendado
    """
    # Verificar permissão
    if not current_user.has_permission(PermissionType.SYSTEM_CONFIG):
        return jsonify({'error': 'Sem permissão para configurar backup'}), 403

    # Obter configurações de agendamento
    data = request.json or {}
    
    try:
        # Configurar backup agendado
        result = BackupService.schedule_backup()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
    
    except Exception as e:
        logging.error(f"Erro ao agendar backup: {e}")
        return jsonify({
            'error': 'Erro ao agendar backup',
            'details': str(e)
        }), 500
