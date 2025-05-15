from flask import Blueprint, render_template, jsonify, request, current_app, session
from flask_login import login_required, current_user
from app.services.service_factory import ServiceFactory
import logging

# Cria o blueprint para rota de visualizações
visualization = Blueprint('visualization', __name__, url_prefix='/diagnostic/visualization')

# Factory para criar serviços
service_factory = ServiceFactory()

@visualization.route('/')
@login_required
def index():
    """Página principal de visualizações"""
    return render_template('diagnostic/visualization.html')

@visualization.route('/cpu_history')
@login_required
def cpu_history():
    """API para dados do gráfico de histórico de CPU"""
    user_id = current_user.id
    limit = request.args.get('limit', 10, type=int)
    
    try:
        # Obtém o serviço de visualização
        visualization_service = service_factory.create_visualization_service()
        
        # Gera o gráfico de histórico de CPU
        chart_data = visualization_service.generate_cpu_history_chart(user_id, limit)
        
        # Verifica se os dados estão vazios
        if not chart_data or 'data' not in chart_data or not chart_data['data']:
            # Retorna um gráfico vazio com mensagem
            empty_chart = {
                'data': [],
                'layout': {
                    'annotations': [
                        {
                            'text': 'Sem dados históricos disponíveis',
                            'xref': 'paper',
                            'yref': 'paper',
                            'showarrow': False,
                            'font': {
                                'size': 16
                            },
                            'x': 0.5,
                            'y': 0.5
                        }
                    ],
                    'title': 'Histórico de Uso de CPU',
                    'xaxis': {'visible': False},
                    'yaxis': {'visible': False}
                }
            }
            return jsonify(empty_chart)
        
        return jsonify(chart_data)
    
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao gerar gráfico de histórico de CPU: {str(e)}", exc_info=True)
        
        # Retorna um gráfico vazio com mensagem de erro
        empty_chart = {
            'data': [],
            'layout': {
                'annotations': [
                    {
                        'text': 'Erro ao carregar dados históricos',
                        'xref': 'paper',
                        'yref': 'paper',
                        'showarrow': False,
                        'font': {
                            'size': 16
                        },
                        'x': 0.5,
                        'y': 0.5
                    }
                ],
                'title': 'Histórico de Uso de CPU',
                'xaxis': {'visible': False},
                'yaxis': {'visible': False}
            }
        }
        return jsonify(empty_chart)

@visualization.route('/memory_history')
@login_required
def memory_history():
    """API para dados do gráfico de histórico de memória"""
    user_id = current_user.id
    limit = request.args.get('limit', 10, type=int)
    
    try:
        # Obtém o serviço de visualização
        visualization_service = service_factory.create_visualization_service()
        
        # Gera o gráfico de histórico de memória
        chart_data = visualization_service.generate_memory_history_chart(user_id, limit)
        
        # Verifica se os dados estão vazios
        if not chart_data or 'data' not in chart_data or not chart_data['data']:
            # Retorna um gráfico vazio com mensagem
            empty_chart = {
                'data': [],
                'layout': {
                    'annotations': [
                        {
                            'text': 'Sem dados históricos disponíveis',
                            'xref': 'paper',
                            'yref': 'paper',
                            'showarrow': False,
                            'font': {
                                'size': 16
                            },
                            'x': 0.5,
                            'y': 0.5
                        }
                    ],
                    'title': 'Histórico de Uso de Memória',
                    'xaxis': {'visible': False},
                    'yaxis': {'visible': False}
                }
            }
            return jsonify(empty_chart)
        
        return jsonify(chart_data)
    
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao gerar gráfico de histórico de memória: {str(e)}", exc_info=True)
        
        # Retorna um gráfico vazio com mensagem de erro
        empty_chart = {
            'data': [],
            'layout': {
                'annotations': [
                    {
                        'text': 'Erro ao carregar dados históricos',
                        'xref': 'paper',
                        'yref': 'paper',
                        'showarrow': False,
                        'font': {
                            'size': 16
                        },
                        'x': 0.5,
                        'y': 0.5
                    }
                ],
                'title': 'Histórico de Uso de Memória',
                'xaxis': {'visible': False},
                'yaxis': {'visible': False}
            }
        }
        return jsonify(empty_chart)

@visualization.route('/disk_history')
@login_required
def disk_history():
    """API para dados do gráfico de histórico de disco"""
    user_id = current_user.id
    limit = request.args.get('limit', 10, type=int)
    
    try:
        # Obtém o serviço de visualização
        visualization_service = service_factory.create_visualization_service()
        
        # Gera o gráfico de histórico de disco
        chart_data = visualization_service.generate_disk_history_chart(user_id, limit)
        
        # Verifica se os dados estão vazios
        if not chart_data or 'data' not in chart_data or not chart_data['data']:
            # Retorna um gráfico vazio com mensagem
            empty_chart = {
                'data': [],
                'layout': {
                    'annotations': [
                        {
                            'text': 'Sem dados históricos disponíveis',
                            'xref': 'paper',
                            'yref': 'paper',
                            'showarrow': False,
                            'font': {
                                'size': 16
                            },
                            'x': 0.5,
                            'y': 0.5
                        }
                    ],
                    'title': 'Histórico de Uso de Disco',
                    'xaxis': {'visible': False},
                    'yaxis': {'visible': False}
                }
            }
            return jsonify(empty_chart)
        
        return jsonify(chart_data)
    
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao gerar gráfico de histórico de disco: {str(e)}", exc_info=True)
        
        # Retorna um gráfico vazio com mensagem de erro
        empty_chart = {
            'data': [],
            'layout': {
                'annotations': [
                    {
                        'text': 'Erro ao carregar dados históricos',
                        'xref': 'paper',
                        'yref': 'paper',
                        'showarrow': False,
                        'font': {
                            'size': 16
                        },
                        'x': 0.5,
                        'y': 0.5
                    }
                ],
                'title': 'Histórico de Uso de Disco',
                'xaxis': {'visible': False},
                'yaxis': {'visible': False}
            }
        }
        return jsonify(empty_chart)

@visualization.route('/health_history')
@login_required
def health_history():
    """API para dados do gráfico de histórico de saúde geral"""
    user_id = current_user.id
    limit = request.args.get('limit', 10, type=int)
    
    try:
        # Obtém o serviço de visualização
        visualization_service = service_factory.create_visualization_service()
        
        # Gera o gráfico de histórico de saúde
        chart_data = visualization_service.generate_health_history_chart(user_id, limit)
        
        # Verifica se os dados estão vazios
        if not chart_data or 'data' not in chart_data or not chart_data['data']:
            # Retorna um gráfico vazio com mensagem
            empty_chart = {
                'data': [],
                'layout': {
                    'annotations': [
                        {
                            'text': 'Sem dados históricos disponíveis',
                            'xref': 'paper',
                            'yref': 'paper',
                            'showarrow': False,
                            'font': {
                                'size': 16
                            },
                            'x': 0.5,
                            'y': 0.5
                        }
                    ],
                    'title': 'Histórico de Saúde do Sistema',
                    'xaxis': {'visible': False},
                    'yaxis': {'visible': False}
                }
            }
            return jsonify(empty_chart)
        
        return jsonify(chart_data)
    
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao gerar gráfico de histórico de saúde: {str(e)}", exc_info=True)
        
        # Retorna um gráfico vazio com mensagem de erro
        empty_chart = {
            'data': [],
            'layout': {
                'annotations': [
                    {
                        'text': 'Erro ao carregar dados históricos',
                        'xref': 'paper',
                        'yref': 'paper',
                        'showarrow': False,
                        'font': {
                            'size': 16
                        },
                        'x': 0.5,
                        'y': 0.5
                    }
                ],
                'title': 'Histórico de Saúde do Sistema',
                'xaxis': {'visible': False},
                'yaxis': {'visible': False}
            }
        }
        return jsonify(empty_chart)

@visualization.route('/problems_by_category')
@login_required
def problems_by_category():
    """API para dados do gráfico de problemas por categoria"""
    user_id = current_user.id
    limit = request.args.get('limit', 10, type=int)
    
    try:
        # Obtém o serviço de visualização
        visualization_service = service_factory.create_visualization_service()
        
        # Gera o gráfico de problemas por categoria
        chart_data = visualization_service.generate_problems_by_category_chart(user_id, limit)
        
        # Verifica se os dados estão vazios
        if not chart_data or 'data' not in chart_data or not chart_data['data']:
            # Retorna um gráfico vazio com mensagem
            empty_chart = {
                'data': [],
                'layout': {
                    'annotations': [
                        {
                            'text': 'Sem dados de problemas disponíveis',
                            'xref': 'paper',
                            'yref': 'paper',
                            'showarrow': False,
                            'font': {
                                'size': 16
                            },
                            'x': 0.5,
                            'y': 0.5
                        }
                    ],
                    'title': 'Problemas por Categoria',
                    'xaxis': {'visible': False},
                    'yaxis': {'visible': False}
                }
            }
            return jsonify(empty_chart)
        
        return jsonify(chart_data)
    
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao gerar gráfico de problemas por categoria: {str(e)}", exc_info=True)
        
        # Retorna um gráfico vazio com mensagem de erro
        empty_chart = {
            'data': [],
            'layout': {
                'annotations': [
                    {
                        'text': 'Erro ao carregar dados de problemas',
                        'xref': 'paper',
                        'yref': 'paper',
                        'showarrow': False,
                        'font': {
                            'size': 16
                        },
                        'x': 0.5,
                        'y': 0.5
                    }
                ],
                'title': 'Problemas por Categoria',
                'xaxis': {'visible': False},
                'yaxis': {'visible': False}
            }
        }
        return jsonify(empty_chart)

@visualization.route('/export/<chart_type>')
@login_required
def export_chart(chart_type):
    """Exporta um gráfico como imagem ou dados CSV/JSON"""
    user_id = current_user.id
    export_format = request.args.get('format', 'json')
    limit = request.args.get('limit', 10, type=int)
    
    # Obtém o serviço de visualização
    visualization_service = service_factory.create_visualization_service()
    
    # Exporta os dados do gráfico
    if chart_type == 'cpu':
        return visualization_service.export_chart_data('cpu', user_id, export_format, limit)
    elif chart_type == 'memory':
        return visualization_service.export_chart_data('memory', user_id, export_format, limit)
    elif chart_type == 'disk':
        return visualization_service.export_chart_data('disk', user_id, export_format, limit)
    elif chart_type == 'health':
        return visualization_service.export_chart_data('health', user_id, export_format, limit)
    elif chart_type == 'problems':
        return visualization_service.export_chart_data('problems', user_id, export_format, limit)
    else:
        return jsonify({'error': 'Tipo de gráfico inválido'}), 400 