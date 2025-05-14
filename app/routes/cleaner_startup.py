from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
import platform
try:
    from app.services.cleaner_service import CleanerService
    from app.services.service_factory import ServiceFactory
except ImportError:
    print("Erro ao importar serviços de limpeza.")

# Criando um novo blueprint
cleaner_startup = Blueprint('cleaner_startup', __name__)

@cleaner_startup.route('/')
@login_required
def index():
    """Página principal da otimização de inicialização"""
    # Verifica se o sistema é Windows
    is_windows = platform.system() == 'Windows'
    
    if not is_windows:
        return render_template('errors/not_supported.html', 
                              feature="Otimização de Inicialização",
                              message="Esta funcionalidade está disponível apenas para Windows.")
    
    try:
        # Obtém o serviço de limpeza
        cleaner_service = ServiceFactory.get_service(CleanerService)
        
        # Obtém itens de inicialização
        startup_items = cleaner_service.analyze_system().get('startup_items', {})
        
        return render_template('cleaner/startup_optimization.html',
                            startup_items=startup_items,
                            title="Otimização de Inicialização")
    except Exception as e:
        return render_template('errors/generic.html', 
                              error=str(e),
                              title="Erro na Otimização de Inicialização")

@cleaner_startup.route('/optimize', methods=['POST'])
@login_required
def optimize_startup():
    """Otimiza a inicialização do sistema desativando itens selecionados"""
    try:
        # Verifica se o sistema é Windows
        if platform.system() != 'Windows':
            return jsonify({'success': False, 'error': 'Esta funcionalidade está disponível apenas para Windows'}), 400
        
        # Obtém os itens selecionados pelo usuário
        items_to_disable = request.json.get('items_to_disable', [])
        
        if not items_to_disable:
            return jsonify({'success': False, 'error': 'Nenhum item selecionado para otimização'}), 400
        
        # Obtém o serviço de limpeza
        cleaner_service = ServiceFactory.get_service(CleanerService)
        
        # Desativa os itens de inicialização selecionados
        result = cleaner_service.optimize_startup(items_to_disable)
        
        return jsonify({
            'success': True, 
            'message': 'Otimização de inicialização concluída com sucesso',
            'disabled_count': len(items_to_disable),
            'details': result
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500