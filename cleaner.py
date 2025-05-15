import json
import os
from pathlib import Path
import time
import uuid
import logging

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
import platform

from app.services.service_factory import ServiceFactory
from app.services.cleaner_service import CleanerService

cleaner = Blueprint('cleaner', __name__)

logger = logging.getLogger(__name__)


@cleaner.route('/')
@login_required
def index():
    """Página principal do módulo de limpeza e otimização"""
    # Verifica se o sistema é Windows
    is_windows = platform.system() == 'Windows'
    
    # Obtém o serviço de limpeza e otimização
    cleaner_service = ServiceFactory.get_service(CleanerService)
    
    # Realiza uma análise básica do sistema
    analysis = cleaner_service.analyze_system()
    
    return render_template('cleaner/index.html', 
                          is_windows=is_windows, 
                          analysis=analysis,
                          title="Limpeza e Otimização")


@cleaner.route('/cleaner/analyze')
@login_required
def analyze_system():
    """Analisa o sistema para limpeza e otimização"""
    try:
        # Cria o serviço de limpeza
        cleaner_service = CleanerService()
        
        # Realiza a análise do sistema
        analysis_result = cleaner_service.analyze_system()
        
        # Formato da resposta baseado no parâmetro 'format'
        response_format = request.args.get('format', 'html')
        
        if response_format == 'json':
            return jsonify(analysis_result)
        else:
            return render_template('cleaner/analysis_results.html', 
                                  analysis_result=analysis_result)
    
    except Exception as e:
        if request.args.get('format') == 'json':
            return jsonify({'error': str(e)}), 500
        else:
            return render_template('errors/500.html', message=str(e)), 500


@cleaner.route('/cleaner/clean-temp', methods=['POST'])
@login_required
def clean_temp_files():
    """Limpa arquivos temporários do sistema"""
    try:
        # Cria o serviço de limpeza
        cleaner_service = CleanerService()
        
        # Limpa arquivos temporários
        result = cleaner_service.clean_temp_files()
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@cleaner.route('/cleaner/clean-browser', methods=['POST'])
@login_required
def clean_browser_cache():
    """Limpa cache e outros dados de navegadores"""
    try:
        # Obtém lista de navegadores para limpar
        browsers = request.json.get('browsers', None)
        
        # Cria o serviço de limpeza
        cleaner_service = CleanerService()
        
        # Limpa cache de navegadores
        result = cleaner_service.clean_browser_cache(browsers)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@cleaner.route('/cleaner/clean-registry', methods=['POST'])
@login_required
def clean_registry():
    """Limpa e repara o registro do Windows"""
    try:
        # Cria o serviço de limpeza
        cleaner_service = CleanerService()
        
        # Limpa o registro
        result = cleaner_service.clean_registry()
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@cleaner.route('/cleaner/optimize-startup', methods=['POST'])
@login_required
def optimize_startup():
    """Otimiza itens de inicialização do Windows"""
    try:
        # Obtém lista de itens para desativar
        items_to_disable = request.json.get('items', None)
        
        # Cria o serviço de limpeza
        cleaner_service = CleanerService()
        
        # Otimiza inicialização
        result = cleaner_service.optimize_startup(items_to_disable)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@cleaner.route('/cleaner/repair-system', methods=['POST'])
@login_required
def repair_system_files():
    """Repara arquivos corrompidos do sistema"""
    try:
        # Cria o serviço de limpeza
        cleaner_service = CleanerService()
        
        # Repara arquivos do sistema
        result = cleaner_service.repair_system_files()
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@cleaner.route('/cleaner/verify-disk', methods=['POST'])
@login_required
def verify_disk():
    """Verifica e repara problemas no disco"""
    try:
        # Cria o serviço de limpeza
        cleaner_service = CleanerService()
        
        # Verifica o disco
        result = cleaner_service.verify_disk()
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@cleaner.route('/cleaner/dashboard')
@login_required
def cleaner_dashboard():
    """Exibe o dashboard de limpeza e otimização"""
    try:
        # Cria o serviço de limpeza
        cleaner_service = CleanerService()
        
        # Realiza a análise do sistema
        analysis_result = cleaner_service.analyze_system()
        
        return render_template('cleaner/dashboard.html', 
                              analysis_result=analysis_result)
    
    except Exception as e:
        return render_template('errors/500.html', message=str(e)), 500


@cleaner.route('/disk_cleanup')
@login_required
def disk_cleanup():
    """Rota para limpeza de disco"""
    # Obtém o serviço de limpeza
    cleaner_service = ServiceFactory.get_service(CleanerService)
    
    return render_template('cleaner/disk_cleanup.html', 
                          title="Limpeza de Disco")


@cleaner.route('/analyze')
@login_required
def analyze():
    """Rota para análise detalhada do sistema"""
    # Obtém o serviço de limpeza
    cleaner_service = ServiceFactory.get_service(CleanerService)
    
    # Realiza a análise
    analysis = cleaner_service.analyze_system()
    
    return render_template('cleaner/analysis_results.html', 
                          analysis=analysis,
                          title="Análise do Sistema")


@cleaner.route('/temp_cleanup')
@login_required
def temp_cleanup():
    """Rota para limpeza de arquivos temporários"""
    # Obtém o serviço de limpeza
    cleaner_service = ServiceFactory.get_service(CleanerService)
    
    return render_template('cleaner/temp_cleanup.html', 
                          title="Limpeza de Temporários")


@cleaner.route('/browser_cleanup')
@login_required
def browser_cleanup():
    """Rota para limpeza de navegadores"""
    # Obtém o serviço de limpeza
    cleaner_service = ServiceFactory.get_service(CleanerService)
    
    # Obtém dados dos navegadores
    browser_data = cleaner_service.analyze_system().get('browser_data', {})
    
    return render_template('cleaner/browser_cleanup.html',
                          browser_data=browser_data,
                          title="Limpeza de Navegadores")


@cleaner.route('/registry_cleanup')
@login_required
def registry_cleanup():
    """Rota para limpeza de registro"""
    # Verifica se o sistema é Windows
    is_windows = platform.system() == 'Windows'
    
    if not is_windows:
        return render_template('errors/not_supported.html', 
                              feature="Limpeza de Registro",
                              message="Esta funcionalidade está disponível apenas para Windows.")
    
    # Obtém o serviço de limpeza
    cleaner_service = ServiceFactory.get_service(CleanerService)
    
    # Obtém análise do registro
    registry_issues = cleaner_service.analyze_system().get('registry_issues', {})
    
    return render_template('cleaner/registry_cleanup.html',
                          registry_issues=registry_issues,
                          title="Limpeza de Registro")


@cleaner.route('/startup_optimization')
@login_required
def startup_optimization():
    """Rota para otimização de inicialização"""
    # Verifica se o sistema é Windows
    is_windows = platform.system() == 'Windows'
    
    if not is_windows:
        return render_template('errors/not_supported.html', 
                              feature="Otimização de Inicialização",
                              message="Esta funcionalidade está disponível apenas para Windows.")
    
    # Obtém o serviço de limpeza
    cleaner_service = ServiceFactory.get_service(CleanerService)
    
    # Obtém itens de inicialização
    startup_items = cleaner_service.analyze_system().get('startup_items', {})
    
    return render_template('cleaner/startup_optimization.html',
                          startup_items=startup_items,
                          title="Otimização de Inicialização")


@cleaner.route('/disk_analyzer')
@login_required
def disk_analyzer():
    """Rota para analisador de disco"""
    # Obtém o serviço de limpeza
    cleaner_service = ServiceFactory.get_service(CleanerService)
    
    # Obtém arquivos grandes
    large_files = cleaner_service.analyze_system().get('large_files', [])
    
    return render_template('cleaner/disk_analyzer.html',
                          large_files=large_files,
                          title="Analisador de Disco")


@cleaner.route('/maintenance_plans')
@login_required
def maintenance_plans():
    """Rota para planos de manutenção programada"""
    # Obtém o serviço de limpeza
    cleaner_service = ServiceFactory.get_service(CleanerService)
    
    return render_template('cleaner/maintenance_plans.html',
                          title="Manutenção Programada")


@cleaner.route('/execute_cleanup', methods=['POST'])
@login_required
def execute_cleanup():
    """API para executar a limpeza do disco"""
    # Obtém as opções de limpeza selecionadas
    options = request.form.getlist('cleanup_options')
    
    # Obtém o serviço de limpeza
    cleaner_service = ServiceFactory.get_service(CleanerService)
    
    # Executa a limpeza com as opções selecionadas
    results = cleaner_service.clean_system(options)
    
    # Se for uma requisição AJAX, retorna JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(results)
    
    # Caso contrário, redireciona para a página de limpeza com uma mensagem
    flash('Limpeza concluída com sucesso!', 'success')
    return redirect(url_for('cleaner.disk_cleanup'))


@cleaner.route('/analyze_disk', methods=['GET', 'POST'])
@login_required
def analyze_disk():
    """
    Rota para executar e exibir resultados da análise de disco.
    Suporta GET e POST:
    - GET: Exibe resultados ou formulário de análise
    - POST: Executa análise baseada nos parâmetros recebidos
    """
    cleaner_service = ServiceFactory.get_service(CleanerService)
    
    # Manipular requisições POST (início de nova análise)
    if request.method == 'POST':
        try:
            # Obter parâmetros da requisição
            if request.is_json:
                data = request.get_json()
                drive = data.get('drive', 'C:')
                include_system = data.get('include_system', False)
                deep_scan = data.get('deep_scan', False)
            else:
                drive = request.form.get('drive', 'C:')
                include_system = request.form.get('include_system') == 'on'
                deep_scan = request.form.get('deep_scan') == 'on'
            
            # Obter informações do disco
            disk_info = cleaner_service._analyze_disk_space()
            
            # Executar a análise
            results = {
                'drive': drive,
                'include_system': include_system,
                'deep_scan': deep_scan,
                'disk_info': disk_info,
                'timestamp': time.time(),
                'large_files': cleaner_service._find_large_files(min_size_mb=50, max_files=100),
                'status': 'completed'
            }
            
            # Gerar ID único para esta análise
            results_id = str(uuid.uuid4())
            
            # Salvar resultado em arquivo temporário para recuperação posterior
            result_dir = Path('data/disk_analysis')
            result_dir.mkdir(parents=True, exist_ok=True)
            
            with open(result_dir / f"{results_id}.json", 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, default=str)
            
            # Se for XHR, retornar ID do resultado
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'results_id': results_id})
            
            # Se for submissão normal de formulário, redirecionar para resultados
            return redirect(url_for('cleaner.analyze_disk', results_id=results_id))
            
        except Exception as e:
            logger.error(f"Erro na análise de disco: {str(e)}", exc_info=True)
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': str(e)}), 500
            flash(f"Erro ao analisar disco: {str(e)}", 'danger')
            return redirect(url_for('cleaner.disk_analyzer'))
    
    # Manipular requisições GET (exibir resultados ou formulário)
    else:
        # Verifica se está solicitando resultados de uma análise prévia
        results_id = request.args.get('results_id')
        
        if results_id:
            # Tenta carregar resultados de análise anterior
            try:
                result_file = Path(f'data/disk_analysis/{results_id}.json')
                
                if not result_file.exists():
                    flash("Resultado de análise não encontrado.", 'warning')
                    return redirect(url_for('cleaner.disk_analyzer'))
                
                with open(result_file, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                
                return render_template('cleaner/disk_analysis_results.html',
                                    results=results,
                                    title="Resultados da Análise de Disco")
            
            except Exception as e:
                logger.error(f"Erro ao carregar resultados de análise: {str(e)}", exc_info=True)
                flash(f"Erro ao carregar resultados: {str(e)}", 'danger')
                return redirect(url_for('cleaner.disk_analyzer'))
        
        # Obtém informações para o formulário de análise
        try:
            # Lista as unidades disponíveis
            disk_info = cleaner_service._analyze_disk_space()
            drives = []
            
            for device, info in disk_info.items():
                # Identifica se é a unidade do sistema
                is_system = (os.environ.get('SYSTEMDRIVE', 'C:').lower() == 
                            info.get('mountpoint', '').lower().rstrip('\\'))
                
                drives.append({
                    'path': info.get('mountpoint', ''),
                    'label': device,
                    'free_space': info.get('formatted_free', '0 B'),
                    'total_space': info.get('formatted_total', '0 B'),
                    'is_system': is_system
                })
            
            # Se não houver drives, adiciona um padrão
            if not drives:
                drives.append({
                    'path': 'C:',
                    'label': 'Disco Principal',
                    'free_space': 'Desconhecido',
                    'total_space': 'Desconhecido',
                    'is_system': True
                })
            
            return render_template('cleaner/disk_analyzer.html',
                                drives=drives,
                                title="Analisador de Disco")
                                
        except Exception as e:
            logger.error(f"Erro ao preparar formulário de análise de disco: {str(e)}", exc_info=True)
            flash(f"Erro ao carregar informações de disco: {str(e)}", 'danger')
            return render_template('cleaner/disk_analyzer.html',
                                drives=[],
                                title="Analisador de Disco")

