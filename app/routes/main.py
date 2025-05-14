from flask import Blueprint, render_template, current_app, request, redirect, url_for, jsonify, session, make_response, flash
from flask_login import current_user, login_required
import platform
import psutil
import os
import datetime
import socket
import logging

# Criar blueprint
main = Blueprint('main', __name__)


@main.route('/')
def index():
    """Rota para a página principal"""
    # Contador de visitas mantido na sessão do usuário
    session['visits'] = session.get('visits', 0) + 1
    
    # Detecção de preferência de tema do sistema, se não houver preferência explícita
    if 'theme' not in session:
        # Verifica o cabeçalho de preferência de tema
        prefers_dark = request.headers.get('Sec-CH-Prefers-Color-Scheme') == 'dark'
        if prefers_dark:
            session['theme'] = 'dark'
        else:
            session['theme'] = 'light'
    
    return render_template(
        'index.html', 
        title='TechCare - Diagnóstico e Manutenção de Computadores',
        current_year=datetime.datetime.now().year
    )


@main.route('/about')
def about():
    """Rota da página sobre"""
    now = datetime.datetime.now()
    return render_template('about.html', now=now)


@main.route('/contact')
def contact():
    """Rota da página de contato"""
    now = datetime.datetime.now()
    return render_template('contact.html', now=now)


@main.route('/theme/<theme>')
def set_theme(theme):
    """Rota para alterar o tema da aplicação (claro/escuro)"""
    # Validação do tema
    if theme not in ['light', 'dark']:
        flash('Tema inválido especificado.', 'warning')
        return redirect(request.referrer or url_for('main.index'))
    
    # Guarda a URL anterior para redirecionamento
    redirect_url = request.referrer or url_for('main.index')
    
    # Guarda o tema nas sessões
    session['theme'] = theme
    
    # Cria a resposta com redirecionamento
    response = make_response(redirect(redirect_url))
    
    # Também guarda o tema nos cookies para persistência
    # Define um cookie de longa duração (365 dias)
    response.set_cookie('theme', theme, max_age=31536000)
    
    return response


@main.route('/set-theme', methods=['POST'])
def set_theme_ajax():
    """Rota para alterar o tema da aplicação via AJAX"""
    # Obtém os dados da requisição
    data = request.get_json()
    theme = data.get('theme')
    
    # Validação do tema
    if theme not in ['light', 'dark']:
        return jsonify({'success': False, 'message': 'Tema inválido especificado'}), 400
    
    # Guarda o tema nas sessões
    session['theme'] = theme
    
    # Prepara a resposta
    response = jsonify({'success': True, 'theme': theme})
    
    # Também guarda o tema nos cookies para persistência
    # Define um cookie de longa duração (365 dias)
    response.set_cookie('theme', theme, max_age=31536000)
    
    return response


@main.route('/set-contrast', methods=['POST'])
def set_contrast():
    """Rota para configurar o modo de alto contraste"""
    # Obtém os dados da requisição
    data = request.get_json()
    high_contrast = data.get('high_contrast', 'false')
    
    # Converte para booleano
    high_contrast = high_contrast.lower() in ['true', 'yes', '1']
    
    # Guarda a preferência nas sessões
    session['high_contrast'] = high_contrast
    
    # Prepara a resposta
    response = jsonify({'success': True, 'high_contrast': high_contrast})
    
    # Também guarda a preferência nos cookies para persistência
    response.set_cookie('high_contrast', str(high_contrast).lower(), max_age=31536000)
    
    return response


def _get_cpu_info():
    try:
        return {
            'cpu_count': psutil.cpu_count(logical=False),
            'logical_cpu_count': psutil.cpu_count(logical=True),
            'cpu_usage': psutil.cpu_percent(interval=1),
            'arch': platform.machine(),
            'processor': platform.processor(),
        }
    except Exception as e:
        return {'error': f'Erro ao coletar CPU: {e}'}

def _get_memory_info():
    try:
        mem = psutil.virtual_memory()
        return {
            'memory_total': round(mem.total / (1024 ** 3), 2),
            'memory_available': round(mem.available / (1024 ** 3), 2),
            'memory_percent': mem.percent
        }
    except Exception as e:
        return {'error': f'Erro ao coletar memória: {e}'}

def _get_disks_info():
    disks = []
    try:
        for partition in psutil.disk_partitions():
            # Exibir apenas partições com letra de unidade (Windows) e acessíveis
            if os.name == 'nt' and (not partition.device or not partition.device[0].isalpha()):
                continue
            if 'cdrom' in partition.opts or partition.fstype == '':
                continue
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info = {
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': round(usage.total / (1024 ** 3), 2),
                    'used': round(usage.used / (1024 ** 3), 2),
                    'free': round(usage.free / (1024 ** 3), 2),
                    'percent': usage.percent
                }
                # Tentar coletar fabricante/modelo (Windows)
                if os.name == 'nt':
                    try:
                        import wmi
                        c = wmi.WMI()
                        for disk in c.Win32_LogicalDisk():
                            if disk.DeviceID == partition.device:
                                disk_info['volume_name'] = getattr(disk, 'VolumeName', None)
                                disk_info['description'] = getattr(disk, 'Description', None)
                    except Exception:
                        pass
                disks.append(disk_info)
            except Exception:
                continue
        return disks
    except Exception as e:
        return [{'error': f'Erro ao coletar discos: {e}'}]

def _get_temperature_info():
    try:
        if hasattr(psutil, 'sensors_temperatures'):
            temps = psutil.sensors_temperatures()
            cpu_temps = temps.get('coretemp') or temps.get('cpu-thermal') or temps.get('acpitz')
            if cpu_temps:
                return max([t.current for t in cpu_temps if hasattr(t, 'current')])
        return 'Indisponível'
    except Exception:
        return 'Indisponível'

def _get_network_info():
    try:
        import socket
        connected = False
        ip = None
        interface = None
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            connected = True
        except Exception:
            connected = False
        # Tentar obter interface e IP
        try:
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            for iface, s in stats.items():
                if s.isup and iface != 'lo':
                    interface = iface
                    for addr in addrs[iface]:
                        if addr.family == socket.AF_INET:
                            ip = addr.address
                            break
                    break
        except Exception:
            pass
        return {'connected': connected, 'interface': interface, 'ip': ip}
    except Exception:
        return {'connected': False, 'interface': None, 'ip': None}

def get_system_snapshot():
    """Coleta informações básicas do sistema para uso em diferentes rotas."""
    info = {
        'os': platform.system(),
        'os_version': platform.version(),
    }
    info.update(_get_cpu_info())
    info.update(_get_memory_info())
    info['disks'] = _get_disks_info()
    info['temperature'] = _get_temperature_info()
    info['network'] = _get_network_info()
    return info


@main.route('/system_info')
@login_required
def system_info():
    """Rota para obter informações básicas do sistema"""
    # Coleta informações básicas do sistema
    info = get_system_snapshot()
    
    # Formato da resposta baseado no parâmetro 'format'
    response_format = request.args.get('format', 'html')
    
    # Adiciona o ano atual para o template
    now = datetime.datetime.now()
    
    if response_format == 'json':
        return jsonify(info)
    else:
        return render_template('system_info.html', info=info, now=now)


@main.route('/set_theme', methods=['POST'])
def set_theme_post():
    """Rota para definir o tema da aplicação através de formulário"""
    theme = request.form.get('theme', 'light')
    # Validação do tema
    if theme not in ['light', 'dark']:
        flash('Tema inválido especificado.', 'warning')
        return redirect(request.referrer or url_for('main.index'))
    
    # Guarda a URL anterior para redirecionamento
    redirect_url = request.referrer or url_for('main.index')
    
    # Guarda o tema nas sessões
    session['theme'] = theme
    
    # Cria a resposta com redirecionamento
    response = make_response(redirect(redirect_url))
    
    # Também guarda o tema nos cookies para persistência
    # Define um cookie de longa duração (365 dias)
    response.set_cookie('theme', theme, max_age=31536000)
    
    return response


@main.route('/dashboard')
@login_required
def dashboard():
    """Rota para o dashboard principal do usuário"""
    # Coleta dados reais do sistema
    sys_info = get_system_snapshot()

    # Cálculo dos percentuais de saúde (quanto menor o uso, melhor)
    cpu_health = max(0, 100 - sys_info.get('cpu_usage', 0))
    memory_health = max(0, 100 - sys_info.get('memory_percent', 0))
    disk_health = 0
    if sys_info['disks']:
        # Média dos percentuais de uso dos discos
        disk_health = max(0, 100 - sum(d['percent'] for d in sys_info['disks'] if 'percent' in d) / len(sys_info['disks']))
    overall_health = round((cpu_health + memory_health + disk_health) / 3, 1)

    dashboard_data = {
        'user_info': {
            'username': 'testuser' if not current_user.is_authenticated else current_user.username,
            'last_login': datetime.datetime.now().isoformat(),
            'total_diagnostics': 5,  # TODO: puxar do histórico real
            'total_repairs': 2       # TODO: puxar do histórico real
        },
        'system_health': {
            'cpu': round(cpu_health, 1),
            'memory': round(memory_health, 1),
            'disk': round(disk_health, 1),
            'overall': overall_health,
            'temperature': sys_info.get('temperature'),
            'network': sys_info.get('network'),
            'cpu_info': {
                'cpu_count': sys_info.get('cpu_count'),
                'logical_cpu_count': sys_info.get('logical_cpu_count'),
                'arch': sys_info.get('arch'),
                'processor': sys_info.get('processor'),
            },
            'memory_info': {
                'total': sys_info.get('memory_total'),
                'available': sys_info.get('memory_available'),
                'percent': sys_info.get('memory_percent'),
            },
            'disks': sys_info.get('disks', [])
        },
        'recent_activities': [
            {
                'type': 'diagnostic',
                'date': (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat(),
                'result': 'Problemas de memória detectados'
            },
            {
                'type': 'repair',
                'date': (datetime.datetime.now() - datetime.timedelta(days=3)).isoformat(),
                'result': 'Limpeza de arquivos temporários concluída'
            }
        ]
    }
    
    return render_template('dashboard.html', data=dashboard_data)


@main.route('/history')
@login_required
def history():
    """Rota para visualizar o histórico de diagnósticos e reparos"""
    # Dados simulados para testes
    history_data = {
        'diagnostics': [
            {
                'id': 'diag-001',
                'date': (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat(),
                'cpu_health': 85,
                'memory_health': 70,
                'disk_health': 65,
                'overall_health': 73
            },
            {
                'id': 'diag-002',
                'date': (datetime.datetime.now() - datetime.timedelta(days=5)).isoformat(),
                'cpu_health': 80,
                'memory_health': 65,
                'disk_health': 60,
                'overall_health': 68
            },
            {
                'id': 'diag-003',
                'date': (datetime.datetime.now() - datetime.timedelta(days=10)).isoformat(),
                'cpu_health': 90,
                'memory_health': 85,
                'disk_health': 75,
                'overall_health': 83
            }
        ],
        'repairs': [
            {
                'id': 'rep-001',
                'date': (datetime.datetime.now() - datetime.timedelta(days=2)).isoformat(),
                'type': 'disk_cleanup',
                'result': 'success',
                'details': 'Liberados 5.2GB de espaço em disco'
            },
            {
                'id': 'rep-002',
                'date': (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat(),
                'type': 'registry_cleanup',
                'result': 'success',
                'details': 'Corrigidas 123 entradas do registro'
            }
        ]
    }
    
    return render_template('history.html', data=history_data)


@main.route('/profile')
@login_required
def profile():
    """Rota para visualizar e editar o perfil do usuário"""
    # Dados simulados para testes
    profile_data = {
        'username': 'testuser' if not current_user.is_authenticated else current_user.username,
        'email': 'test@example.com',
        'role': 'user',
        'created_at': (datetime.datetime.now() - datetime.timedelta(days=30)).isoformat(),
        'last_login': datetime.datetime.now().isoformat(),
        'preferences': {
            'theme': session.get('theme', 'light'),
            'notifications': True,
            'auto_scan': False
        }
    }
    
    return render_template('profile.html', data=profile_data) 