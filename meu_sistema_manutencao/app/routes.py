from flask import Blueprint, render_template
from flask_login import login_required
from app.controllers.service_controller import service_bp
from app.controllers.service_log_controller import service_log_bp
from app.controllers.system_metric_controller import system_metric_bp
from app.controllers.notification_controller import notification_bp
from app.controllers.audit_log_controller import audit_log_bp
from app.controllers.audit_log_retention_controller import audit_log_retention_bp
from app.controllers.audit_log_query_controller import audit_log_query_bp
from app.controllers.audit_log_export_controller import audit_log_export_bp
from app.controllers.audit_log_anomaly_notification_controller import audit_log_anomaly_notification_bp
from app.controllers.user_role_controller import user_role_bp
from app.controllers.user_activity_controller import user_activity_bp
from app.controllers.service_monitoring_controller import service_monitoring_bp
from app.controllers.service_management_controller import service_management_bp
from app.controllers.system_config_controller import system_config_bp
from app.controllers.dashboard_controller import dashboard_bp
from app.controllers.user_management_controller import user_management_bp
from app.controllers.backup_controller import backup_bp

def register_blueprints(app):
    """
    Registrar todos os blueprints da aplicação
    """
    # Blueprints de serviços
    app.register_blueprint(service_bp, url_prefix='/services')
    app.register_blueprint(service_log_bp, url_prefix='/services')
    
    # Blueprints de métricas
    app.register_blueprint(system_metric_bp, url_prefix='/metrics')
    
    # Blueprints de notificações
    app.register_blueprint(notification_bp, url_prefix='/notifications')
    app.register_blueprint(audit_log_bp, url_prefix='/audit-logs')
    app.register_blueprint(audit_log_retention_bp, url_prefix='/audit-logs/retention')
    app.register_blueprint(audit_log_query_bp, url_prefix='/audit-logs/query')
    app.register_blueprint(audit_log_export_bp, url_prefix='/audit-logs/export')
    app.register_blueprint(audit_log_anomaly_notification_bp, url_prefix='/audit-logs/anomalies')
    app.register_blueprint(user_role_bp, url_prefix='/users')
    app.register_blueprint(user_activity_bp, url_prefix='/user-activities')
    app.register_blueprint(service_monitoring_bp, url_prefix='/services')
    app.register_blueprint(service_management_bp, url_prefix='/services/management')
    app.register_blueprint(system_config_bp, url_prefix='/system/config')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(user_management_bp, url_prefix='/users')
    app.register_blueprint(backup_bp, url_prefix='/system/backup')

    return app

# Rotas adicionais
@app.route('/admin/audit-log-analysis')
@login_required
def audit_log_analysis():
    """
    Renderizar template de análise de logs de auditoria
    """
    return render_template('admin/audit_log_analysis.html')
