from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
import platform
import os
import datetime
import json
from pathlib import Path

from app.services.service_factory import ServiceFactory
from app.services.driver_update_service import DriverUpdateService
from app.services.repair_service import RepairService

drivers = Blueprint('drivers', __name__)

@drivers.route('/')
@login_required
def index():
    """Rota principal da página de drivers"""
    # Verifica se o sistema é Windows
    is_windows = platform.system() == 'Windows'
    
    # Obtém o serviço de atualização de drivers
    driver_service = ServiceFactory.get_service(DriverUpdateService)
    
    # Se não for Windows, retorna a página com aviso de sistema não suportado
    if not is_windows:
        flash('A atualização de drivers é suportada apenas para Windows.', 'warning')
        return render_template('drivers/index.html', is_windows=False, drivers_info={})
    
    # Verifica se deve escanear os drivers
    scan_requested = request.args.get('scan', 'false').lower() == 'true'
    
    if scan_requested:
        # Escaneia os drivers do sistema
        drivers_info = driver_service.scan_drivers()
    else:
        # Carrega a última verificação, se disponível
        cache_file = Path("data/drivers/last_scan.json")
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    drivers_info = json.load(f)
            except:
                drivers_info = {}
        else:
            drivers_info = {}
    
    return render_template('drivers/index.html', is_windows=is_windows, drivers_info=drivers_info)


@drivers.route('/scan_drivers')
@login_required
def scan_drivers_page():
    """Rota para a página de escaneamento de drivers"""
    # Verifica se o sistema é Windows
    is_windows = platform.system() == 'Windows'
    
    if not is_windows:
        flash('A atualização de drivers é suportada apenas para Windows.', 'warning')
        return redirect(url_for('drivers.index'))
    
    # Obtém o serviço de atualização de drivers
    driver_service = ServiceFactory.get_service(DriverUpdateService)
    
    # Define o modo de teste para ambiente de desenvolvimento
    test_mode = 'development' in current_app.config['ENV']
    if test_mode:
        os.environ['DRIVER_TEST_MODE'] = '1'
    
    # Escaneia os drivers do sistema
    drivers_info = driver_service.scan_drivers()
    
    # Remove a variável de ambiente de teste
    if test_mode:
        if 'DRIVER_TEST_MODE' in os.environ:
            del os.environ['DRIVER_TEST_MODE']
    
    # Salva a verificação no cache
    cache_file = Path("data/drivers/last_scan.json")
    cache_file.parent.mkdir(exist_ok=True, parents=True)
    
    with open(cache_file, 'w') as f:
        json.dump(drivers_info, f)
    
    flash('Escaneamento de drivers concluído.', 'success')
    return render_template('drivers/index.html', is_windows=is_windows, drivers_info=drivers_info)


@drivers.route('/details/<driver_id>')
@login_required
def driver_details(driver_id):
    """Rota para visualizar detalhes de um driver"""
    # Verifica se o sistema é Windows
    is_windows = platform.system() == 'Windows'
    
    if not is_windows:
        flash('A atualização de drivers é suportada apenas para Windows.', 'warning')
        return redirect(url_for('drivers.index'))
    
    # Obtém o serviço de atualização de drivers
    driver_service = ServiceFactory.get_service(DriverUpdateService)
    
    # Obtém os detalhes do driver
    driver_details = driver_service.get_driver_details(driver_id)
    
    return render_template('drivers/details.html', driver=driver_details)


@drivers.route('/api/details/<driver_id>')
@login_required
def api_driver_details(driver_id):
    """API para obter detalhes de um driver"""
    # Obtém o serviço de atualização de drivers
    driver_service = ServiceFactory.get_service(DriverUpdateService)
    
    # Obtém os detalhes do driver
    driver_details = driver_service.get_driver_details(driver_id)
    
    return jsonify(driver_details)


@drivers.route('/api/history')
@login_required
def api_driver_history():
    """API para obter histórico de atualizações de drivers"""
    # Obtém o serviço de atualização de drivers
    driver_service = ServiceFactory.get_service(DriverUpdateService)
    
    # Obtém o número máximo de registros
    limit = request.args.get('limit', 10, type=int)
    
    # Obtém o histórico de atualizações
    history = driver_service.get_update_history(limit=limit)
    
    return jsonify({
        'success': True,
        'history': history
    })


@drivers.route('/drivers/update/<string:driver_id>', methods=['POST'])
@login_required
def update_driver(driver_id):
    """Atualiza um driver específico"""
    try:
        # Obtém informações da atualização do formulário
        update_info = request.form.get('update_info')
        if update_info:
            update_info = json.loads(update_info)
        else:
            return jsonify({'error': 'Informações de atualização não fornecidas'}), 400
        
        # Cria o serviço de atualização de drivers
        driver_service = DriverUpdateService()
        
        # Baixa o driver
        download_result = driver_service.download_driver(driver_id, update_info)
        
        if not download_result['success']:
            return jsonify({
                'success': False,
                'step': 'download',
                'error': download_result.get('error', 'Falha ao baixar o driver')
            }), 400
        
        # Instala o driver
        install_result = driver_service.install_driver(download_result)
        
        return jsonify({
            'success': install_result['success'],
            'step': 'install',
            'restart_required': install_result.get('restart_required', False),
            'message': install_result.get('message', ''),
            'error': install_result.get('error', '')
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@drivers.route('/drivers/update-all', methods=['POST'])
@login_required
def update_all_drivers():
    """Atualiza todos os drivers desatualizados"""
    try:
        # Cria o serviço de atualização de drivers
        driver_service = DriverUpdateService()
        
        # Atualiza todos os drivers
        update_result = driver_service.update_all_drivers()
        
        return jsonify(update_result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@drivers.route('/drivers/dashboard')
@login_required
def driver_dashboard():
    """Exibe o dashboard de atualização de drivers"""
    try:
        # Cria o serviço de atualização de drivers
        driver_service = DriverUpdateService()
        
        # Realiza o escaneamento
        scan_result = driver_service.scan_drivers()
        
        return render_template('drivers/dashboard.html', 
                              scan_result=scan_result)
    
    except Exception as e:
        return render_template('errors/500.html', message=str(e)), 500


# Rotas da API para drivers
@drivers.route('/api/drivers/scan', methods=['GET'])
@login_required
def api_scan_drivers():
    """API para escanear drivers do sistema"""
    try:
        service = DriverUpdateService()
        results = service.scan_drivers()
        
        return jsonify({
            'success': True,
            'results': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
@drivers.route('/api/drivers/download/<driver_id>', methods=['POST'])
@login_required
def api_download_driver(driver_id):
    """API para baixar um driver específico"""
    try:
        service = DriverUpdateService()
        result = service.download_driver(driver_id)
        
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
@drivers.route('/api/drivers/install/<driver_id>', methods=['POST'])
@login_required
def api_install_driver(driver_id):
    """API para instalar um driver baixado"""
    try:
        data = request.get_json() or {}
        file_path = data.get('file_path')
        
        if not file_path:
            return jsonify({
                'success': False,
                'error': 'O caminho do arquivo é obrigatório'
            }), 400
            
        service = DriverUpdateService()
        result = service.install_driver(driver_id, file_path)
        
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@drivers.route('/api/drivers/details/<driver_id>')
@login_required
def api_drivers_details(driver_id):
    """API para obter detalhes de um driver"""
    try:
        service = DriverUpdateService()
        driver = service.get_driver_details(driver_id)
        
        return jsonify({
            'success': True,
            'driver': driver
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@drivers.route('/api/drivers/history')
@login_required
def api_drivers_history():
    """API para obter histórico de atualizações de drivers"""
    try:
        service = DriverUpdateService()
        limit = request.args.get('limit', 10, type=int)
        history = service.get_update_history(limit=limit)
        
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@drivers.route('/api/repair/plan/<plan_id>', methods=['GET'])
@login_required
def get_repair_plan_api(plan_id):
    """API para obter um plano de reparo"""
    # Obtém o serviço de reparo
    repair_service = ServiceFactory.get_service(RepairService) 