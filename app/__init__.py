from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import datetime
import os
import sys
import logging
from pathlib import Path

from config import config

# Configuração de logging
logger = logging.getLogger(__name__)

# Detecta o ambiente
IS_WINDOWS = sys.platform.startswith('win')
IS_TESTING = 'pytest' in sys.modules or 'unittest' in sys.modules

# Tratamento para módulos específicos do Windows
try:
    if IS_WINDOWS:
        import wmi
        import win32com.client
        logger.info("Módulos do Windows importados com sucesso.")
    else:
        logger.warning("Ambiente não-Windows detectado. Simulando módulos Windows se necessário.")
except ImportError:
    logger.warning("Módulos do Windows (wmi, win32com) não puderam ser importados.")

# Inicialização das extensões
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def datetime_filter(value, format="%d/%m/%Y %H:%M"):
    """Formata um timestamp ou objeto datetime para exibição"""
    if not value:
        return ""
    
    if isinstance(value, (int, float)):
        # Timestamp em segundos
        import datetime
        value = datetime.datetime.fromtimestamp(value)
        
    return value.strftime(format)

def create_app(config_name='default'):
    """
    Função factory para criar a aplicação Flask
    
    Args:
        config_name: Nome da configuração a ser usada (default, development, testing, production)
        
    Returns:
        Aplicação Flask configurada
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Registra o filtro datetime
    app.jinja_env.filters['datetime'] = datetime_filter
    
    # Inicialização das extensões com a aplicação
    db.init_app(app)
    login_manager.init_app(app)
    
    # Configuração dos serviços e repositórios
    setup_services(app)
    
    # Registro dos blueprints
    register_blueprints(app)
    
    # Criar todas as tabelas do banco de dados
    with app.app_context():
        db.create_all()
    
    # Adiciona variáveis de contexto para todos os templates
    @app.context_processor
    def inject_now():
        return {'now': datetime.datetime.now()}
    
    # Handlers globais de erro
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html', message=str(e)), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html', message=str(e)), 500

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html', message=str(e)), 403

    return app

def register_blueprints(app):
    """
    Registra todos os blueprints na aplicação
    
    Args:
        app: Instância da aplicação Flask
    """
    from app.routes.main import main
    app.register_blueprint(main)
    
    from app.routes.diagnostic import diagnostic
    app.register_blueprint(diagnostic, url_prefix='/diagnostic')
    
    from app.routes.diagnostic_analysis import diagnostic_analysis
    app.register_blueprint(diagnostic_analysis, url_prefix='/diagnostic/analysis')
    
    from app.routes.diagnostic_overview import diagnostic_overview
    app.register_blueprint(diagnostic_overview, url_prefix='/diagnostic/overview')
    
    from app.routes.diagnostic_visualization import visualization
    app.register_blueprint(visualization, url_prefix='/diagnostic/visualization')
    
    from app.routes.auth import auth
    app.register_blueprint(auth)
    
    from app.routes.repair import repair
    app.register_blueprint(repair, url_prefix='/repair')
    
    from app.routes.drivers import drivers
    app.register_blueprint(drivers, url_prefix='/drivers')
    
    from app.routes.cleaner import cleaner
    app.register_blueprint(cleaner, url_prefix='/cleaner')
    
    from app.routes.cleaner_analysis import cleaner_analysis
    app.register_blueprint(cleaner_analysis, url_prefix='/cleaner/analysis')
    
    from app.routes.cleaner_cleaning import cleaner_cleaning
    app.register_blueprint(cleaner_cleaning, url_prefix='/cleaner/cleaning')
    
    from app.routes.cleaner_maintenance import cleaner_maintenance
    app.register_blueprint(cleaner_maintenance, url_prefix='/cleaner/maintenance')
    
    from app.routes.cleaner_startup import cleaner_startup
    app.register_blueprint(cleaner_startup, url_prefix='/cleaner/startup')
    
    from app.routes.api import api
    app.register_blueprint(api, url_prefix='/api')

def setup_services(app):
    """
    Configura os serviços e repositórios da aplicação
    
    Args:
        app: Aplicação Flask
    """
    # Importações aqui para evitar circular imports
    from app.services.service_factory import ServiceFactory
    from app.services.diagnostic_repository import DiagnosticRepository
    
    # Configura o caminho para armazenamento de diagnósticos
    diagnostics_path = app.config.get('DIAGNOSTICS_STORAGE_PATH', os.path.join(app.instance_path, 'diagnostics'))
    
    # Cria o diretório se não existir
    os.makedirs(diagnostics_path, exist_ok=True)
    
    # Cria e registra o repositório de diagnósticos
    diagnostic_repository = DiagnosticRepository(diagnostics_path)
    
    # Registra o repositório como dependência para o serviço de diagnóstico
    ServiceFactory.register_dependency(
        'DiagnosticService', 
        'diagnostic_repository', 
        diagnostic_repository
    ) 