import logging
import sys
import plotly
import plotly.graph_objects as go
import plotly.express as px
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from flask import Response, send_file
import io
import csv
import tempfile
import os

from app.services.diagnostic_repository import DiagnosticRepository

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class VisualizationService:
    """
    Serviço responsável por gerar visualizações gráficas para histórico de diagnósticos.
    Utiliza Plotly para criar gráficos interativos que podem ser incorporados na interface web.
    """
    
    def __init__(self, diagnostic_repository: Optional[DiagnosticRepository] = None):
        """
        Inicializa o serviço de visualização
        
        Args:
            diagnostic_repository: Repositório para obter dados históricos de diagnósticos
        """
        # Injeção de dependência do repositório
        self.repository = diagnostic_repository or DiagnosticRepository()
        logger.info("Iniciando VisualizationService")
    
    def generate_cpu_history_chart(self, user_id: str, limit: int = 10) -> dict:
        """
        Gera um gráfico de linha do histórico de uso de CPU
        
        Args:
            user_id: ID do usuário para obter os diagnósticos
            limit: Número de registros históricos a considerar
            
        Returns:
            dict: JSON do gráfico Plotly
        """
        logger.info(f"Gerando gráfico de histórico de CPU para usuário {user_id}")
        history = self.repository.get_history(user_id, limit)
        
        if not history:
            logger.warning("Nenhum dado histórico encontrado para gerar o gráfico")
            # Retorna um gráfico vazio com mensagem
            fig = go.Figure()
            fig.add_annotation(
                text="Sem dados históricos disponíveis",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return json.loads(fig.to_json())
        
        # Preparar dados para o gráfico
        dates = []
        cpu_usage = []
        
        for item in history:
            try:
                # Converte timestamp para objeto datetime
                if 'timestamp' in item:
                    timestamp = item['timestamp']
                    if isinstance(timestamp, str):
                        date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        dates.append(date)
                    else:
                        dates.append(datetime.now())  # Fallback
                else:
                    dates.append(datetime.now())  # Fallback
                
                # Extrai uso de CPU
                if 'cpu' in item and 'usage' in item['cpu']:
                    cpu_usage.append(item['cpu']['usage'])
                else:
                    cpu_usage.append(None)  # Valor ausente
            except Exception as e:
                logger.error(f"Erro ao processar item do histórico: {e}")
                continue
        
        # Criar DataFrame para plotly
        df = pd.DataFrame({
            'data': dates,
            'uso_cpu': cpu_usage
        })
        
        # Criar gráfico
        fig = px.line(
            df, 
            x='data', 
            y='uso_cpu',
            labels={'uso_cpu': 'Uso de CPU (%)', 'data': 'Data'},
            title='Histórico de Uso de CPU',
            markers=True
        )
        
        # Adicionar linha de tendência
        fig.add_trace(
            go.Scatter(
                x=df['data'],
                y=df['uso_cpu'].rolling(window=min(3, len(df)), min_periods=1).mean(),
                mode='lines',
                line=dict(color='red', dash='dash'),
                name='Tendência'
            )
        )
        
        # Configurar layout
        fig.update_layout(
            xaxis_title='Data',
            yaxis_title='Uso de CPU (%)',
            yaxis=dict(range=[0, 100]),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            margin=dict(l=20, r=20, t=40, b=20),
            height=400
        )
        
        return json.loads(fig.to_json())
    
    def generate_memory_history_chart(self, user_id: str, limit: int = 10) -> dict:
        """
        Gera um gráfico de linha do histórico de uso de memória
        
        Args:
            user_id: ID do usuário para obter os diagnósticos
            limit: Número de registros históricos a considerar
            
        Returns:
            dict: JSON do gráfico Plotly
        """
        logger.info(f"Gerando gráfico de histórico de memória para usuário {user_id}")
        history = self.repository.get_history(user_id, limit)
        
        if not history:
            logger.warning("Nenhum dado histórico encontrado para gerar o gráfico")
            # Retorna um gráfico vazio com mensagem
            fig = go.Figure()
            fig.add_annotation(
                text="Sem dados históricos disponíveis",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return json.loads(fig.to_json())
        
        # Preparar dados para o gráfico
        dates = []
        memory_usage = []
        
        for item in history:
            try:
                # Converte timestamp para objeto datetime
                if 'timestamp' in item:
                    timestamp = item['timestamp']
                    if isinstance(timestamp, str):
                        date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        dates.append(date)
                    else:
                        dates.append(datetime.now())  # Fallback
                else:
                    dates.append(datetime.now())  # Fallback
                
                # Extrai uso de memória
                if 'memory' in item and 'usage' in item['memory']:
                    memory_usage.append(item['memory']['usage'])
                else:
                    memory_usage.append(None)  # Valor ausente
            except Exception as e:
                logger.error(f"Erro ao processar item do histórico: {e}")
                continue
        
        # Criar DataFrame para plotly
        df = pd.DataFrame({
            'data': dates,
            'uso_memoria': memory_usage
        })
        
        # Criar gráfico
        fig = px.line(
            df, 
            x='data', 
            y='uso_memoria',
            labels={'uso_memoria': 'Uso de Memória (%)', 'data': 'Data'},
            title='Histórico de Uso de Memória',
            markers=True
        )
        
        # Adicionar linha de tendência
        fig.add_trace(
            go.Scatter(
                x=df['data'],
                y=df['uso_memoria'].rolling(window=min(3, len(df)), min_periods=1).mean(),
                mode='lines',
                line=dict(color='red', dash='dash'),
                name='Tendência'
            )
        )
        
        # Configurar layout
        fig.update_layout(
            xaxis_title='Data',
            yaxis_title='Uso de Memória (%)',
            yaxis=dict(range=[0, 100]),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            margin=dict(l=20, r=20, t=40, b=20),
            height=400
        )
        
        return json.loads(fig.to_json())
    
    def generate_disk_history_chart(self, user_id: str, limit: int = 10) -> dict:
        """
        Gera um gráfico de linha do histórico de uso de disco
        
        Args:
            user_id: ID do usuário para obter os diagnósticos
            limit: Número de registros históricos a considerar
            
        Returns:
            dict: JSON do gráfico Plotly
        """
        logger.info(f"Gerando gráfico de histórico de disco para usuário {user_id}")
        history = self.repository.get_history(user_id, limit)
        
        if not history:
            logger.warning("Nenhum dado histórico encontrado para gerar o gráfico")
            # Retorna um gráfico vazio com mensagem
            fig = go.Figure()
            fig.add_annotation(
                text="Sem dados históricos disponíveis",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return json.loads(fig.to_json())
        
        # Preparar dados para o gráfico
        dates = []
        disk_usage = []
        
        for item in history:
            try:
                # Converte timestamp para objeto datetime
                if 'timestamp' in item:
                    timestamp = item['timestamp']
                    if isinstance(timestamp, str):
                        date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        dates.append(date)
                    else:
                        dates.append(datetime.now())  # Fallback
                else:
                    dates.append(datetime.now())  # Fallback
                
                # Extrai uso de disco
                if 'disk' in item and 'usage' in item['disk']:
                    disk_usage.append(item['disk']['usage'])
                else:
                    disk_usage.append(None)  # Valor ausente
            except Exception as e:
                logger.error(f"Erro ao processar item do histórico: {e}")
                continue
        
        # Criar DataFrame para plotly
        df = pd.DataFrame({
            'data': dates,
            'uso_disco': disk_usage
        })
        
        # Criar gráfico
        fig = px.line(
            df, 
            x='data', 
            y='uso_disco',
            labels={'uso_disco': 'Uso de Disco (%)', 'data': 'Data'},
            title='Histórico de Uso de Disco',
            markers=True
        )
        
        # Adicionar linha de tendência
        fig.add_trace(
            go.Scatter(
                x=df['data'],
                y=df['uso_disco'].rolling(window=min(3, len(df)), min_periods=1).mean(),
                mode='lines',
                line=dict(color='red', dash='dash'),
                name='Tendência'
            )
        )
        
        # Configurar layout
        fig.update_layout(
            xaxis_title='Data',
            yaxis_title='Uso de Disco (%)',
            yaxis=dict(range=[0, 100]),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            margin=dict(l=20, r=20, t=40, b=20),
            height=400
        )
        
        return json.loads(fig.to_json())
    
    def generate_overall_health_chart(self, user_id: str, limit: int = 10) -> dict:
        """
        Gera um gráfico de linha da pontuação geral de saúde do sistema
        
        Args:
            user_id: ID do usuário para obter os diagnósticos
            limit: Número de registros históricos a considerar
            
        Returns:
            dict: JSON do gráfico Plotly
        """
        logger.info(f"Gerando gráfico de saúde geral para usuário {user_id}")
        history = self.repository.get_history(user_id, limit)
        
        if not history:
            logger.warning("Nenhum dado histórico encontrado para gerar o gráfico")
            # Retorna um gráfico vazio com mensagem
            fig = go.Figure()
            fig.add_annotation(
                text="Sem dados históricos disponíveis",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return json.loads(fig.to_json())
        
        # Preparar dados para o gráfico
        dates = []
        scores = []
        
        for item in history:
            try:
                # Converte timestamp para objeto datetime
                if 'timestamp' in item:
                    timestamp = item['timestamp']
                    if isinstance(timestamp, str):
                        date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        dates.append(date)
                    else:
                        dates.append(datetime.now())  # Fallback
                else:
                    dates.append(datetime.now())  # Fallback
                
                # Extrai pontuação geral
                if 'score' in item:
                    scores.append(item['score'])
                else:
                    scores.append(None)  # Valor ausente
            except Exception as e:
                logger.error(f"Erro ao processar item do histórico: {e}")
                continue
        
        # Criar DataFrame para plotly
        df = pd.DataFrame({
            'data': dates,
            'pontuacao': scores
        })
        
        # Definir cores com base na pontuação
        colors = []
        for score in scores:
            if score is None:
                colors.append('gray')
            elif score >= 90:
                colors.append('green')
            elif score >= 70:
                colors.append('yellow')
            elif score >= 50:
                colors.append('orange')
            else:
                colors.append('red')
        
        # Criar gráfico
        fig = go.Figure()
        
        # Adicionar linha principal
        fig.add_trace(
            go.Scatter(
                x=df['data'],
                y=df['pontuacao'],
                mode='lines+markers',
                name='Pontuação de Saúde',
                line=dict(color='blue', width=2),
                marker=dict(color=colors, size=10)
            )
        )
        
        # Adicionar linha de tendência
        fig.add_trace(
            go.Scatter(
                x=df['data'],
                y=df['pontuacao'].rolling(window=min(3, len(df)), min_periods=1).mean(),
                mode='lines',
                line=dict(color='black', dash='dash'),
                name='Tendência'
            )
        )
        
        # Adicionar áreas de referência
        fig.add_hrect(y0=90, y1=100, fillcolor="green", opacity=0.1, line_width=0)
        fig.add_hrect(y0=70, y1=90, fillcolor="yellow", opacity=0.1, line_width=0)
        fig.add_hrect(y0=50, y1=70, fillcolor="orange", opacity=0.1, line_width=0)
        fig.add_hrect(y0=0, y1=50, fillcolor="red", opacity=0.1, line_width=0)
        
        # Configurar layout
        fig.update_layout(
            title='Evolução da Saúde do Sistema',
            xaxis_title='Data',
            yaxis_title='Pontuação de Saúde (0-100)',
            yaxis=dict(range=[0, 100]),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            margin=dict(l=20, r=20, t=50, b=20),
            height=400,
            hovermode='x'
        )
        
        return json.loads(fig.to_json())
    
    def generate_problems_by_category(self, user_id: str, limit: int = 10) -> dict:
        """
        Gera um gráfico de barras com problemas agrupados por categoria
        
        Args:
            user_id: ID do usuário para obter os diagnósticos
            limit: Número de registros históricos a considerar
            
        Returns:
            dict: JSON do gráfico Plotly
        """
        logger.info(f"Gerando gráfico de problemas por categoria para usuário {user_id}")
        history = self.repository.get_history(user_id, limit)
        
        if not history:
            logger.warning("Nenhum dado histórico encontrado para gerar o gráfico")
            # Retorna um gráfico vazio com mensagem
            fig = go.Figure()
            fig.add_annotation(
                text="Sem dados históricos disponíveis",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return json.loads(fig.to_json())
        
        # Contador de problemas por categoria
        problems_by_category = {}
        
        for item in history:
            try:
                if 'problems' in item and isinstance(item['problems'], list):
                    for problem in item['problems']:
                        if 'category' in problem:
                            category = problem['category']
                            if category in problems_by_category:
                                problems_by_category[category] += 1
                            else:
                                problems_by_category[category] = 1
            except Exception as e:
                logger.error(f"Erro ao processar problemas do histórico: {e}")
                continue
        
        # Se não houver problemas, retorna gráfico com mensagem
        if not problems_by_category:
            fig = go.Figure()
            fig.add_annotation(
                text="Nenhum problema encontrado no histórico",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return json.loads(fig.to_json())
        
        # Criar DataFrame para plotly
        categories = list(problems_by_category.keys())
        counts = list(problems_by_category.values())
        
        # Definir cores para categorias
        colors = {
            'cpu': 'rgb(55, 83, 109)',
            'memory': 'rgb(26, 118, 255)',
            'disk': 'rgb(178, 86, 0)',
            'network': 'rgb(0, 128, 0)',
            'security': 'rgb(204, 0, 0)',
            'drivers': 'rgb(102, 0, 204)',
            'startup': 'rgb(204, 102, 0)',
            'temperature': 'rgb(255, 0, 0)',
        }
        
        bar_colors = [colors.get(cat, 'rgb(128, 128, 128)') for cat in categories]
        
        # Criar gráfico
        fig = go.Figure(data=[
            go.Bar(
                x=categories,
                y=counts,
                marker_color=bar_colors
            )
        ])
        
        # Configurar layout
        fig.update_layout(
            title='Problemas por Categoria',
            xaxis_title='Categoria',
            yaxis_title='Número de Problemas',
            margin=dict(l=20, r=20, t=50, b=20),
            height=400
        )
        
        return json.loads(fig.to_json())
    
    def generate_health_history_chart(self, user_id: str, limit: int = 10) -> dict:
        """
        Gera um gráfico de linha da pontuação geral de saúde do sistema
        
        Args:
            user_id: ID do usuário para obter os diagnósticos
            limit: Número de registros históricos a considerar
            
        Returns:
            dict: JSON do gráfico Plotly
        """
        logger.info(f"Gerando gráfico de saúde geral para usuário {user_id}")
        # Usar o método renomeado
        return self.generate_overall_health_chart(user_id, limit)
    
    def generate_problems_by_category_chart(self, user_id: str, limit: int = 10) -> dict:
        """
        Gera um gráfico de barras com problemas agrupados por categoria
        
        Args:
            user_id: ID do usuário para obter os diagnósticos
            limit: Número de registros históricos a considerar
            
        Returns:
            dict: JSON do gráfico Plotly
        """
        logger.info(f"Gerando gráfico de problemas por categoria para usuário {user_id}")
        # Usar o método existente
        return self.generate_problems_by_category(user_id, limit)
    
    def export_chart_data(self, chart_type: str, user_id: str, export_format: str = 'json', limit: int = 10) -> Response:
        """
        Exporta os dados de um gráfico em formato CSV, JSON ou PNG
        
        Args:
            chart_type: Tipo de gráfico (cpu, memory, disk, health, problems)
            user_id: ID do usuário para obter os diagnósticos
            export_format: Formato de exportação (csv, json ou png)
            limit: Número de registros históricos a considerar
            
        Returns:
            Response: Resposta HTTP com o arquivo para download
        """
        logger.info(f"Exportando dados do gráfico {chart_type} no formato {export_format}")
        
        # Obter os dados históricos
        history = self.repository.get_history(user_id, limit)
        
        if not history:
            # Retornar erro se não houver dados
            return Response(
                json.dumps({"error": "Sem dados históricos disponíveis"}),
                mimetype='application/json',
                status=404
            )
        
        # Preparar dataframe conforme o tipo de gráfico
        if chart_type == 'cpu':
            df = self._prepare_cpu_dataframe(history)
            filename = f"cpu_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            title = "Histórico de CPU"
        elif chart_type == 'memory':
            df = self._prepare_memory_dataframe(history)
            filename = f"memory_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            title = "Histórico de Memória"
        elif chart_type == 'disk':
            df = self._prepare_disk_dataframe(history)
            filename = f"disk_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            title = "Histórico de Disco"
        elif chart_type == 'health':
            df = self._prepare_health_dataframe(history)
            filename = f"health_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            title = "Histórico de Saúde do Sistema"
        elif chart_type == 'problems':
            df = self._prepare_problems_dataframe(history)
            filename = f"problems_by_category_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            title = "Problemas por Categoria"
        else:
            # Tipo de gráfico inválido
            return Response(
                json.dumps({"error": "Tipo de gráfico inválido"}),
                mimetype='application/json',
                status=400
            )
        
        # Exportar no formato solicitado
        if export_format == 'csv':
            # Preparar buffer para CSV
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, quoting=csv.QUOTE_NONNUMERIC)
            csv_buffer.seek(0)
            
            # Retornar como download
            return Response(
                csv_buffer.getvalue(),
                mimetype='text/csv',
                headers={
                    'Content-Disposition': f'attachment; filename="{filename}.csv"'
                }
            )
        
        elif export_format == 'json':
            # Converter dataframe para JSON
            json_data = df.to_json(orient='records', date_format='iso')
            
            # Retornar como download
            return Response(
                json_data,
                mimetype='application/json',
                headers={
                    'Content-Disposition': f'attachment; filename="{filename}.json"'
                }
            )
        
        elif export_format == 'png':
            # Gerar uma imagem do gráfico
            try:
                # Criar figura apropriada para o tipo de gráfico
                if chart_type == 'problems':
                    # Gráfico de barras para problemas
                    fig = px.bar(
                        df, 
                        x='categoria', 
                        y='contagem',
                        title=title,
                        labels={'categoria': 'Categoria', 'contagem': 'Número de Problemas'}
                    )
                else:
                    # Gráfico de linha para os demais tipos
                    y_col = df.columns[1]  # Segunda coluna contém os valores
                    fig = px.line(
                        df, 
                        x='data', 
                        y=y_col,
                        title=title,
                        markers=True
                    )
                
                # Criar arquivo temporário para a imagem
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp:
                    temp_filename = temp.name
                    fig.write_image(temp_filename, format='png')
                
                # Enviar arquivo e configurar para exclusão após envio
                return send_file(
                    temp_filename,
                    mimetype='image/png',
                    as_attachment=True,
                    download_name=f"{filename}.png",
                    # Configurar callback para remover o arquivo após o envio
                    # Esta feature não está disponível no Flask < 2.0, então usamos try/except
                    _after_request=lambda _: os.unlink(temp_filename) 
                )
            
            except Exception as e:
                logger.error(f"Erro ao gerar imagem PNG: {e}")
                # Remover arquivo temporário em caso de erro
                if 'temp_filename' in locals():
                    try:
                        os.unlink(temp_filename)
                    except:
                        pass
                
                return Response(
                    json.dumps({"error": f"Erro ao gerar imagem: {str(e)}"}),
                    mimetype='application/json',
                    status=500
                )
        
        else:
            # Formato inválido
            return Response(
                json.dumps({"error": "Formato de exportação inválido"}),
                mimetype='application/json',
                status=400
            )
    
    def _prepare_cpu_dataframe(self, history: List[Dict]) -> pd.DataFrame:
        """Prepara DataFrame para dados de CPU"""
        dates = []
        cpu_usage = []
        
        for item in history:
            try:
                # Extrair timestamp
                if 'timestamp' in item:
                    timestamp = item['timestamp']
                    if isinstance(timestamp, str):
                        date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        dates.append(date)
                    else:
                        dates.append(datetime.now())
                else:
                    dates.append(datetime.now())
                
                # Extrair uso de CPU
                if 'cpu' in item and 'usage' in item['cpu']:
                    cpu_usage.append(item['cpu']['usage'])
                else:
                    cpu_usage.append(None)
            except Exception as e:
                logger.error(f"Erro ao processar item do histórico: {e}")
                continue
        
        return pd.DataFrame({
            'data': dates,
            'uso_cpu': cpu_usage
        })
    
    def _prepare_memory_dataframe(self, history: List[Dict]) -> pd.DataFrame:
        """Prepara DataFrame para dados de memória"""
        dates = []
        memory_usage = []
        
        for item in history:
            try:
                # Extrair timestamp
                if 'timestamp' in item:
                    timestamp = item['timestamp']
                    if isinstance(timestamp, str):
                        date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        dates.append(date)
                    else:
                        dates.append(datetime.now())
                else:
                    dates.append(datetime.now())
                
                # Extrair uso de memória
                if 'memory' in item and 'usage' in item['memory']:
                    memory_usage.append(item['memory']['usage'])
                else:
                    memory_usage.append(None)
            except Exception as e:
                logger.error(f"Erro ao processar item do histórico: {e}")
                continue
        
        return pd.DataFrame({
            'data': dates,
            'uso_memoria': memory_usage
        })
    
    def _prepare_disk_dataframe(self, history: List[Dict]) -> pd.DataFrame:
        """Prepara DataFrame para dados de disco"""
        dates = []
        disk_usage = []
        
        for item in history:
            try:
                # Extrair timestamp
                if 'timestamp' in item:
                    timestamp = item['timestamp']
                    if isinstance(timestamp, str):
                        date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        dates.append(date)
                    else:
                        dates.append(datetime.now())
                else:
                    dates.append(datetime.now())
                
                # Extrair uso de disco
                if 'disk' in item and 'usage' in item['disk']:
                    disk_usage.append(item['disk']['usage'])
                else:
                    disk_usage.append(None)
            except Exception as e:
                logger.error(f"Erro ao processar item do histórico: {e}")
                continue
        
        return pd.DataFrame({
            'data': dates,
            'uso_disco': disk_usage
        })
    
    def _prepare_health_dataframe(self, history: List[Dict]) -> pd.DataFrame:
        """Prepara DataFrame para dados de saúde geral"""
        dates = []
        scores = []
        
        for item in history:
            try:
                # Extrair timestamp
                if 'timestamp' in item:
                    timestamp = item['timestamp']
                    if isinstance(timestamp, str):
                        date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        dates.append(date)
                    else:
                        dates.append(datetime.now())
                else:
                    dates.append(datetime.now())
                
                # Extrair pontuação geral
                if 'score' in item:
                    scores.append(item['score'])
                else:
                    scores.append(None)
            except Exception as e:
                logger.error(f"Erro ao processar item do histórico: {e}")
                continue
        
        return pd.DataFrame({
            'data': dates,
            'pontuacao': scores
        })
    
    def _prepare_problems_dataframe(self, history: List[Dict]) -> pd.DataFrame:
        """Prepara DataFrame para dados de problemas por categoria"""
        problems_count = {}
        
        for item in history:
            try:
                if 'problems' in item and isinstance(item['problems'], list):
                    for problem in item['problems']:
                        if 'category' in problem:
                            category = problem['category']
                            if category in problems_count:
                                problems_count[category] += 1
                            else:
                                problems_count[category] = 1
            except Exception as e:
                logger.error(f"Erro ao processar problemas do histórico: {e}")
                continue
        
        categories = list(problems_count.keys())
        counts = list(problems_count.values())
        
        return pd.DataFrame({
            'categoria': categories,
            'contagem': counts
        }) 