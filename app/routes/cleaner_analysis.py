from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
import platform
from app.services.cleaner_service import CleanerService

# Criando um novo blueprint
cleaner_analysis = Blueprint('cleaner_analysis', __name__)

@cleaner_analysis.route('/')
@login_required
def index():
    """Página principal do módulo de análise de limpeza"""
    is_windows = platform.system() == 'Windows'
    cleaner_service = CleanerService()
    analysis = cleaner_service.analyze_system()
    return render_template('cleaner/analysis/index.html', is_windows=is_windows, analysis=analysis, title="Análise do Sistema")

@cleaner_analysis.route('/analyze')
@login_required
def analyze_system():
    try:
        cleaner_service = CleanerService()
        analysis_result = cleaner_service.analyze_system()
        response_format = request.args.get('format', 'html')
        if response_format == 'json':
            return jsonify(analysis_result)
        else:
            return render_template('cleaner/analysis/results.html', analysis_result=analysis_result)
    except Exception as e:
        if request.args.get('format') == 'json':
            return jsonify({'error': str(e)}), 500
        else:
            return render_template('errors/500.html', message=str(e)), 500

@cleaner_analysis.route('/dashboard')
@login_required
def cleaner_dashboard():
    try:
        cleaner_service = CleanerService()
        analysis_result = cleaner_service.analyze_system()
        return render_template('cleaner/analysis/dashboard.html', analysis_result=analysis_result)
    except Exception as e:
        return render_template('errors/500.html', message=str(e)), 500

@cleaner_analysis.route('/results')
@login_required
def analysis_results():
    cleaner_service = CleanerService()
    analysis = cleaner_service.analyze_system()
    return render_template('cleaner/analysis/results.html', analysis=analysis, title="Resultados da Análise")

@cleaner_analysis.route('/disk')
@login_required
def disk_analyzer():
    cleaner_service = CleanerService()
    large_files = cleaner_service.analyze_system().get('large_files', [])
    return render_template('cleaner/analysis/disk.html', large_files=large_files, title="Analisador de Disco")

@cleaner_analysis.route('/browser')
@login_required
def browser_analyzer():
    cleaner_service = CleanerService()
    browser_data = cleaner_service.analyze_system().get('browser_data', {})
    return render_template('cleaner/analysis/browser.html', browser_data=browser_data, title="Análise de Navegadores")

@cleaner_analysis.route('/registry')
@login_required
def registry_analyzer():
    is_windows = platform.system() == 'Windows'
    if not is_windows:
        return render_template('errors/not_supported.html', feature="Análise de Registro", message="Esta funcionalidade está disponível apenas para Windows.")
    cleaner_service = CleanerService()
    registry_issues = cleaner_service.analyze_system().get('registry_issues', {})
    return render_template('cleaner/analysis/registry.html', registry_issues=registry_issues, title="Análise de Registro")

@cleaner_analysis.route('/startup')
@login_required
def startup_analyzer():
    is_windows = platform.system() == 'Windows'
    if not is_windows:
        return render_template('errors/not_supported.html', feature="Análise de Inicialização", message="Esta funcionalidade está disponível apenas para Windows.")
    cleaner_service = CleanerService()
    startup_items = cleaner_service.analyze_system().get('startup_items', {})
    return render_template('cleaner/analysis/startup.html', startup_items=startup_items, title="Análise de Inicialização") 