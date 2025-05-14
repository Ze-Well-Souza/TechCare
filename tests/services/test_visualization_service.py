import unittest
from unittest.mock import MagicMock, patch
import json
import pandas as pd
from datetime import datetime

from app.services.visualization_service import VisualizationService
from app.services.diagnostic_repository import DiagnosticRepository

class TestVisualizationService(unittest.TestCase):
    """Testes para o serviço de visualização"""
    
    def setUp(self):
        """Configuração para cada teste"""
        # Mock do repositório de diagnóstico
        self.mock_repository = MagicMock(spec=DiagnosticRepository)
        
        # Dados simulados para testes
        self.sample_history = [
            {
                'timestamp': '2024-06-01T10:00:00',
                'cpu': {'usage': 45, 'temperature': 60},
                'memory': {'usage': 65, 'available': 8192},
                'disk': {'usage': 75, 'free': 100000},
                'score': 85,
                'problems': [
                    {'category': 'cpu', 'description': 'CPU usage high'},
                    {'category': 'memory', 'description': 'Memory fragmentation'}
                ]
            },
            {
                'timestamp': '2024-06-02T10:00:00',
                'cpu': {'usage': 35, 'temperature': 55},
                'memory': {'usage': 55, 'available': 9000},
                'disk': {'usage': 70, 'free': 110000},
                'score': 90,
                'problems': [
                    {'category': 'disk', 'description': 'Disk fragmentation'}
                ]
            },
            {
                'timestamp': '2024-06-03T10:00:00',
                'cpu': {'usage': 60, 'temperature': 65},
                'memory': {'usage': 75, 'available': 6000},
                'disk': {'usage': 80, 'free': 90000},
                'score': 70,
                'problems': [
                    {'category': 'cpu', 'description': 'CPU throttling'},
                    {'category': 'memory', 'description': 'Low memory'},
                    {'category': 'network', 'description': 'Network latency'}
                ]
            }
        ]
        
        # Configurar o mock para retornar os dados simulados
        self.mock_repository.get_history.return_value = self.sample_history
        
        # Instanciar o serviço com o repositório mockado
        self.service = VisualizationService(diagnostic_repository=self.mock_repository)

    def test_generate_cpu_history_chart(self):
        """Teste de geração de gráfico de CPU"""
        # Chamar o método
        result = self.service.generate_cpu_history_chart('user123', 10)
        
        # Verificar que o repositório foi chamado corretamente
        self.mock_repository.get_history.assert_called_once_with('user123', 10)
        
        # Verificar que o resultado é um dict (JSON)
        self.assertIsInstance(result, dict)
        
        # Verificar que contém os elementos esperados do Plotly
        self.assertIn('data', result)
        self.assertIn('layout', result)
        
        # Verificar que os dados contêm as séries esperadas
        data = result['data']
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)  # Pelo menos 1 série (linha principal)

    def test_generate_memory_history_chart(self):
        """Teste de geração de gráfico de memória"""
        # Chamar o método
        result = self.service.generate_memory_history_chart('user123', 10)
        
        # Verificar que o repositório foi chamado corretamente
        self.mock_repository.get_history.assert_called_once_with('user123', 10)
        
        # Verificar que o resultado é um dict (JSON)
        self.assertIsInstance(result, dict)
        self.assertIn('data', result)
        self.assertIn('layout', result)

    def test_generate_disk_history_chart(self):
        """Teste de geração de gráfico de disco"""
        # Chamar o método
        result = self.service.generate_disk_history_chart('user123', 10)
        
        # Verificar estrutura do resultado
        self.assertIsInstance(result, dict)
        self.assertIn('data', result)
        self.assertIn('layout', result)

    def test_generate_health_history_chart(self):
        """Teste de geração de gráfico de saúde geral"""
        # Mock para o método subjacente
        self.service.generate_overall_health_chart = MagicMock(return_value={'data': [], 'layout': {}})
        
        # Chamar o método
        result = self.service.generate_health_history_chart('user123', 10)
        
        # Verificar que o método subjacente foi chamado
        self.service.generate_overall_health_chart.assert_called_once_with('user123', 10)
        
        # Verificar resultado
        self.assertEqual(result, {'data': [], 'layout': {}})

    def test_generate_problems_by_category_chart(self):
        """Teste de geração de gráfico de problemas por categoria"""
        # Mock para o método subjacente
        self.service.generate_problems_by_category = MagicMock(return_value={'data': [], 'layout': {}})
        
        # Chamar o método
        result = self.service.generate_problems_by_category_chart('user123', 10)
        
        # Verificar que o método subjacente foi chamado
        self.service.generate_problems_by_category.assert_called_once_with('user123', 10)
        
        # Verificar resultado
        self.assertEqual(result, {'data': [], 'layout': {}})

    def test_empty_history(self):
        """Teste com histórico vazio"""
        # Configurar mock para retornar lista vazia
        self.mock_repository.get_history.return_value = []
        
        # Chamar o método
        result = self.service.generate_cpu_history_chart('user123', 10)
        
        # Verificar que foi retornado um gráfico vazio com mensagem
        self.assertIsInstance(result, dict)
        self.assertIn('layout', result)
        self.assertIn('annotations', result['layout'])
        self.assertEqual(len(result['layout']['annotations']), 1)
        self.assertIn('text', result['layout']['annotations'][0])
        self.assertEqual(result['layout']['annotations'][0]['text'], 'Sem dados históricos disponíveis')

    def test_prepare_dataframes(self):
        """Teste de preparação de dataframes para gráficos"""
        # Testar cada método de preparação de dataframe
        cpu_df = self.service._prepare_cpu_dataframe(self.sample_history)
        memory_df = self.service._prepare_memory_dataframe(self.sample_history)
        disk_df = self.service._prepare_disk_dataframe(self.sample_history)
        health_df = self.service._prepare_health_dataframe(self.sample_history)
        problems_df = self.service._prepare_problems_dataframe(self.sample_history)
        
        # Verificar que são dataframes
        self.assertIsInstance(cpu_df, pd.DataFrame)
        self.assertIsInstance(memory_df, pd.DataFrame)
        self.assertIsInstance(disk_df, pd.DataFrame)
        self.assertIsInstance(health_df, pd.DataFrame)
        self.assertIsInstance(problems_df, pd.DataFrame)
        
        # Verificar que possuem as colunas esperadas
        self.assertIn('data', cpu_df.columns)
        self.assertIn('uso_cpu', cpu_df.columns)
        
        self.assertIn('data', memory_df.columns)
        self.assertIn('uso_memoria', memory_df.columns)
        
        self.assertIn('data', disk_df.columns)
        self.assertIn('uso_disco', disk_df.columns)
        
        self.assertIn('data', health_df.columns)
        self.assertIn('pontuacao', health_df.columns)
        
        self.assertIn('categoria', problems_df.columns)
        self.assertIn('contagem', problems_df.columns)
        
        # Verificar número de linhas
        self.assertEqual(len(cpu_df), 3)
        self.assertEqual(len(memory_df), 3)
        self.assertEqual(len(disk_df), 3)
        self.assertEqual(len(health_df), 3)
        
        # Verificar problemas por categoria (cpu:2, memory:2, disk:1, network:1)
        categories = problems_df['categoria'].tolist()
        counts = problems_df['contagem'].tolist()
        
        self.assertIn('cpu', categories)
        self.assertIn('memory', categories)
        self.assertIn('disk', categories)
        self.assertIn('network', categories)
        
        cpu_index = categories.index('cpu')
        self.assertEqual(counts[cpu_index], 2)
        
        memory_index = categories.index('memory')
        self.assertEqual(counts[memory_index], 2)

    def test_export_chart_data(self):
        """Teste de exportação de dados de gráfico"""
        # Patch para as respostas Flask
        with patch('app.services.visualization_service.Response') as mock_response, \
             patch('app.services.visualization_service.send_file') as mock_send_file:
            
            # Configurar mock_response
            mock_response.return_value = "CSV Response"
            
            # Testar exportação CSV
            result = self.service.export_chart_data('cpu', 'user123', 'csv', 10)
            self.assertEqual(result, "CSV Response")
            
            # Verificar que Response foi chamado com os argumentos corretos
            args, kwargs = mock_response.call_args
            self.assertIn('text/csv', kwargs['mimetype'])
            self.assertIn('attachment', kwargs['headers']['Content-Disposition'])
            
            # Resetar mock
            mock_response.reset_mock()
            mock_response.return_value = "JSON Response"
            
            # Testar exportação JSON
            result = self.service.export_chart_data('memory', 'user123', 'json', 10)
            self.assertEqual(result, "JSON Response")
            
            # Verificar que Response foi chamado com os argumentos corretos
            args, kwargs = mock_response.call_args
            self.assertIn('application/json', kwargs['mimetype'])
            self.assertIn('attachment', kwargs['headers']['Content-Disposition'])

    def test_invalid_export_format(self):
        """Teste com formato de exportação inválido"""
        # Patch para as respostas Flask
        with patch('app.services.visualization_service.Response') as mock_response:
            mock_response.return_value = "Error Response"
            
            # Chamar com formato inválido
            result = self.service.export_chart_data('cpu', 'user123', 'invalid', 10)
            self.assertEqual(result, "Error Response")
            
            # Verificar que Response foi chamado com erro
            args, kwargs = mock_response.call_args
            self.assertEqual(kwargs['status'], 400)
            self.assertIn('error', json.loads(args[0]))

    def test_invalid_chart_type(self):
        """Teste com tipo de gráfico inválido"""
        # Patch para as respostas Flask
        with patch('app.services.visualization_service.Response') as mock_response:
            mock_response.return_value = "Error Response"
            
            # Chamar com tipo inválido
            result = self.service.export_chart_data('invalid', 'user123', 'csv', 10)
            self.assertEqual(result, "Error Response")
            
            # Verificar que Response foi chamado com erro
            args, kwargs = mock_response.call_args
            self.assertEqual(kwargs['status'], 400)
            self.assertIn('error', json.loads(args[0]))
            
if __name__ == '__main__':
    unittest.main() 