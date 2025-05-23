from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
import platform
from app.services.cleaner_service import CleanerService

# Criando um novo blueprint
cleaner_cleaning = Blueprint('cleaner_cleaning', __name__)

@cleaner_cleaning.route('/')
@login_required
def index():
    """Página principal do módulo de limpeza"""
    is_windows = platform.system() == 'Windows'
    cleaner_service = CleanerService()
    cleaning_options = cleaner_service.get_cleaning_options()
    return render_template('cleaner/cleaning/index.html', is_windows=is_windows, cleaning_options=cleaning_options, title="Limpeza do Sistema")

@cleaner_cleaning.route('/execute', methods=['POST'])
@login_required
def execute_cleaning():
    try:
        options = request.form.getlist('cleaning_options')
        cleaner_service = CleanerService()
        result = cleaner_service.clean_system(options)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(result)
        else:
            flash('Limpeza realizada com sucesso!', 'success')
            return redirect(url_for('cleaner_cleaning.index'))
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': str(e)}), 500
        else:
            flash(f'Erro durante a limpeza: {str(e)}', 'danger')
            return redirect(url_for('cleaner_cleaning.index'))

@cleaner_cleaning.route('/temp_files')
@login_required
def temp_files():
    """Página de limpeza de arquivos temporários"""
    cleaner_service = CleanerService()
    temp_files = cleaner_service.get_temp_files()
    return render_template('cleaner/cleaning/temp_files.html', temp_files=temp_files, title="Arquivos Temporários")

@cleaner_cleaning.route('/browser_cache')
@login_required
def browser_cache():
    """Página de limpeza de cache de navegadores"""
    cleaner_service = CleanerService()
    browser_cache = cleaner_service.get_browser_cache()
    return render_template('cleaner/cleaning/browser_cache.html', browser_cache=browser_cache, title="Cache de Navegadores")

@cleaner_cleaning.route('/duplicates')
@login_required
def duplicates():
    """Página de limpeza de arquivos duplicados"""
    cleaner_service = CleanerService()
    duplicates = cleaner_service.get_duplicate_files()
    return render_template('cleaner/cleaning/duplicates.html', duplicates=duplicates, title="Arquivos Duplicados")

@cleaner_cleaning.route('/system_logs')
@login_required
def system_logs():
    """Página de limpeza de logs do sistema"""
    is_windows = platform.system() == 'Windows'
    if not is_windows:
        return render_template('errors/not_supported.html', feature="Limpeza de Logs do Sistema", message="Esta funcionalidade está disponível apenas para Windows.")
    cleaner_service = CleanerService()
    system_logs = cleaner_service.get_system_logs()
    return render_template('cleaner/cleaning/system_logs.html', system_logs=system_logs, title="Logs do Sistema")

@cleaner_cleaning.route('/recycle_bin')
@login_required
def recycle_bin():
    """Página para esvaziar a lixeira"""
    is_windows = platform.system() == 'Windows'
    if not is_windows:
        return render_template('errors/not_supported.html', feature="Limpeza da Lixeira", message="Esta funcionalidade está disponível apenas para Windows.")
    
    return render_template('cleaner/cleaning/recycle_bin.html', title="Esvaziar Lixeira")

@cleaner_cleaning.route('/recycle_bin/empty', methods=['POST'])
@login_required
def empty_recycle_bin():
    """Esvazia a lixeira"""
    try:
        cleaner_service = CleanerService()
        result = cleaner_service.empty_recycle_bin()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(result)
        else:
            if result.get('success', False):
                flash('Lixeira esvaziada com sucesso!', 'success')
            else:
                flash(f'Erro ao esvaziar a lixeira: {result.get("error", "Erro desconhecido")}', 'danger')
            return redirect(url_for('cleaner_cleaning.recycle_bin'))
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': str(e)}), 500
        else:
            flash(f'Erro ao esvaziar a lixeira: {str(e)}', 'danger')
            return redirect(url_for('cleaner_cleaning.recycle_bin'))

@cleaner_cleaning.route('/downloads')
@login_required
def downloads_folder():
    """Página para limpar a pasta de downloads"""
    is_windows = platform.system() == 'Windows'
    if not is_windows:
        return render_template('errors/not_supported.html', feature="Limpeza da Pasta de Downloads", message="Esta funcionalidade está disponível apenas para Windows.")
    
    return render_template('cleaner/cleaning/downloads.html', title="Limpar Pasta de Downloads")

@cleaner_cleaning.route('/downloads/clean', methods=['POST'])
@login_required
def clean_downloads():
    """Limpa a pasta de downloads"""
    try:
        cleaner_service = CleanerService()
        result = cleaner_service.clean_downloads_folder()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(result)
        else:
            if result.get('success', False):
                flash('Pasta de downloads limpa com sucesso!', 'success')
            else:
                flash(f'Erro ao limpar a pasta de downloads: {result.get("error", "Erro desconhecido")}', 'danger')
            return redirect(url_for('cleaner_cleaning.downloads_folder'))
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': str(e)}), 500
        else:
            flash(f'Erro ao limpar a pasta de downloads: {str(e)}', 'danger')
            return redirect(url_for('cleaner_cleaning.downloads_folder')) 