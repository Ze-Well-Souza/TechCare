from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.services.cleaner_service import CleanerService

# Criando um novo blueprint
cleaner_maintenance = Blueprint('cleaner_maintenance', __name__)

@cleaner_maintenance.route('/')
@login_required
def index():
    cleaner_service = CleanerService()
    return render_template('cleaner/maintenance/index.html', title="Manutenção do Sistema")

@cleaner_maintenance.route('/disk_cleanup')
@login_required
def disk_cleanup():
    cleaner_service = CleanerService()
    return render_template('cleaner/maintenance/disk_cleanup.html', title="Limpeza de Disco")

@cleaner_maintenance.route('/temp_cleanup')
@login_required
def temp_cleanup():
    cleaner_service = CleanerService()
    return render_template('cleaner/maintenance/temp_cleanup.html', title="Limpeza de Temporários")

@cleaner_maintenance.route('/maintenance_plans')
@login_required
def maintenance_plans():
    cleaner_service = CleanerService()
    return render_template('cleaner/maintenance/maintenance_plans.html', title="Manutenção Programada")

@cleaner_maintenance.route('/browser_cleanup')
@login_required
def browser_cleanup():
    cleaner_service = CleanerService()
    return render_template('cleaner/maintenance/browser_cleanup.html', title="Limpeza de Navegadores")

@cleaner_maintenance.route('/registry_cleanup')
@login_required
def registry_cleanup():
    cleaner_service = CleanerService()
    return render_template('cleaner/maintenance/registry_cleanup.html', title="Limpeza de Registro")

@cleaner_maintenance.route('/startup_optimization')
@login_required
def startup_optimization():
    cleaner_service = CleanerService()
    return render_template('cleaner/maintenance/startup_optimization.html', title="Otimização de Inicialização")

@cleaner_maintenance.route('/disk_analyzer')
@login_required
def disk_analyzer():
    cleaner_service = CleanerService()
    return render_template('cleaner/maintenance/disk_analyzer.html', title="Analisador de Disco")

@cleaner_maintenance.route('/analyze')
@login_required
def analyze():
    cleaner_service = CleanerService()
    return render_template('cleaner/maintenance/analyze.html', title="Análise Detalhada") 