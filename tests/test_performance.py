"""
Testes de carga e performance para verificar a escalabilidade do sistema.

Estes testes são projetados para medir o desempenho da aplicação
sob diferentes níveis de carga e identificar possíveis gargalos.
"""
import pytest
import time
import threading
import queue
import statistics
from concurrent.futures import ThreadPoolExecutor
from flask import url_for

class TestPerformance:
    """
    Testes de performance para a aplicação TechCare.
    """
    
    def test_endpoint_response_time(self, client):
        """Testa o tempo de resposta de endpoints críticos"""
        # Lista de endpoints para testar (caminhos relativos)
        endpoints = [
            '/',  # Página inicial
            '/login',  # Página de login
            '/register',  # Página de registro
            '/about',  # Página sobre
        ]
        
        results = {}
        
        # Testa cada endpoint
        for endpoint in endpoints:
            start_time = time.time()
            response = client.get(endpoint)
            end_time = time.time()
            
            # Calcula o tempo de resposta em milissegundos
            response_time = (end_time - start_time) * 1000
            
            # Armazena os resultados
            results[endpoint] = {
                'status_code': response.status_code,
                'response_time_ms': response_time
            }
            
            # Verifica se a resposta foi bem-sucedida
            assert response.status_code in [200, 302], f"Endpoint {endpoint} retornou status {response.status_code}"
            
            # Verifica se o tempo de resposta está dentro de limites aceitáveis
            assert response_time < 500, f"Tempo de resposta para {endpoint} muito alto: {response_time:.2f}ms"
        
        # Imprime os resultados para análise
        print("\nTempos de resposta dos endpoints:")
        for endpoint, data in results.items():
            print(f"{endpoint}: {data['response_time_ms']:.2f}ms (Status: {data['status_code']})")
    
    def test_concurrent_requests(self, client):
        """Testa a capacidade de lidar com múltiplas requisições simultâneas"""
        # Número de requisições concorrentes
        num_concurrent = 10
        # Endpoint a ser testado
        endpoint = '/'
        
        # Fila para armazenar os resultados
        results_queue = queue.Queue()
        
        def make_request():
            """Função que faz a requisição e armazena o resultado"""
            start_time = time.time()
            response = client.get(endpoint)
            end_time = time.time()
            
            results_queue.put({
                'status_code': response.status_code,
                'response_time_ms': (end_time - start_time) * 1000
            })
        
        # Cria e inicia as threads
        threads = []
        for _ in range(num_concurrent):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Espera todas as threads terminarem
        for thread in threads:
            thread.join()
        
        # Coleta os resultados
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        # Calcula estatísticas
        response_times = [r['response_time_ms'] for r in results]
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        # Verifica se todos os requests foram bem-sucedidos
        for i, result in enumerate(results):
            assert result['status_code'] in [200, 302], f"Request {i} falhou com status {result['status_code']}"
        
        # Verifica se o tempo médio de resposta está dentro de limites aceitáveis
        assert avg_response_time < 1000, f"Tempo médio de resposta muito alto: {avg_response_time:.2f}ms"
        
        # Imprime os resultados para análise
        print(f"\nTeste de concorrência ({num_concurrent} requests simultâneos):")
        print(f"Tempo médio: {avg_response_time:.2f}ms")
        print(f"Tempo máximo: {max_response_time:.2f}ms")
        print(f"Tempo mínimo: {min_response_time:.2f}ms")
    
    def test_api_endpoint_performance(self, client, auth):
        """Testa o desempenho dos endpoints de API"""
        # Faz login
        auth.login()
        
        # Lista de endpoints de API para testar
        api_endpoints = [
            '/api/diagnostic/summary',  # Resumo de diagnósticos
            '/api/system/info',  # Informações do sistema
            '/api/drivers/list',  # Lista de drivers
        ]
        
        results = {}
        
        # Testa cada endpoint
        for endpoint in api_endpoints:
            start_time = time.time()
            response = client.get(endpoint)
            end_time = time.time()
            
            # Calcula o tempo de resposta em milissegundos
            response_time = (end_time - start_time) * 1000
            
            # Armazena os resultados
            results[endpoint] = {
                'status_code': response.status_code,
                'response_time_ms': response_time
            }
            
            # Verifica se a resposta foi bem-sucedida
            assert response.status_code in [200, 302], f"API endpoint {endpoint} retornou status {response.status_code}"
            
            # Verifica se o tempo de resposta está dentro de limites aceitáveis para APIs
            assert response_time < 300, f"Tempo de resposta para API {endpoint} muito alto: {response_time:.2f}ms"
        
        # Imprime os resultados para análise
        print("\nTempos de resposta dos endpoints de API:")
        for endpoint, data in results.items():
            print(f"{endpoint}: {data['response_time_ms']:.2f}ms (Status: {data['status_code']})")
    
    def test_load_testing_with_multiple_requests(self, client):
        """Testa a aplicação sob carga simulada com múltiplas requisições sequenciais"""
        # Endpoint a ser testado
        endpoint = '/'
        # Número de requisições
        num_requests = 50
        
        response_times = []
        status_codes = []
        
        # Faz múltiplas requisições sequenciais
        for i in range(num_requests):
            start_time = time.time()
            response = client.get(endpoint)
            end_time = time.time()
            
            # Armazena os resultados
            status_codes.append(response.status_code)
            response_times.append((end_time - start_time) * 1000)
        
        # Calcula estatísticas
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        # Verifica se todas as requisições foram bem-sucedidas
        success_rate = sum(1 for code in status_codes if code in [200, 302]) / len(status_codes)
        assert success_rate >= 0.95, f"Taxa de sucesso muito baixa: {success_rate:.2%}"
        
        # Verifica se o tempo médio de resposta está dentro de limites aceitáveis
        assert avg_response_time < 500, f"Tempo médio de resposta muito alto: {avg_response_time:.2f}ms"
        
        # Imprime os resultados para análise
        print(f"\nTeste de carga ({num_requests} requisições sequenciais):")
        print(f"Taxa de sucesso: {success_rate:.2%}")
        print(f"Tempo médio: {avg_response_time:.2f}ms")
        print(f"Tempo máximo: {max_response_time:.2f}ms")
        print(f"Tempo mínimo: {min_response_time:.2f}ms")
    
    def test_database_query_performance(self, client, auth):
        """Testa o desempenho de consultas ao banco de dados"""
        # Faz login
        auth.login()
        
        # Endpoints que envolvem consultas ao banco de dados
        db_endpoints = [
            '/dashboard',  # Dashboard com dados do usuário
            '/history',  # Histórico de diagnósticos
            '/profile',  # Perfil do usuário
        ]
        
        results = {}
        
        # Testa cada endpoint
        for endpoint in db_endpoints:
            start_time = time.time()
            response = client.get(endpoint)
            end_time = time.time()
            
            # Calcula o tempo de resposta em milissegundos
            response_time = (end_time - start_time) * 1000
            
            # Armazena os resultados
            results[endpoint] = {
                'status_code': response.status_code,
                'response_time_ms': response_time
            }
            
            # Verifica se a resposta foi bem-sucedida
            assert response.status_code in [200, 302], f"DB endpoint {endpoint} retornou status {response.status_code}"
            
            # Verifica se o tempo de resposta está dentro de limites aceitáveis
            assert response_time < 500, f"Tempo de resposta para DB {endpoint} muito alto: {response_time:.2f}ms"
        
        # Imprime os resultados para análise
        print("\nTempos de resposta para endpoints com consultas ao banco de dados:")
        for endpoint, data in results.items():
            print(f"{endpoint}: {data['response_time_ms']:.2f}ms (Status: {data['status_code']})")
    
    def test_static_file_performance(self, client):
        """Testa o desempenho da entrega de arquivos estáticos"""
        # Lista de arquivos estáticos para testar
        static_files = [
            '/static/css/styles.css',
            '/static/js/scripts.js',
            '/static/img/logo_small.svg',
        ]
        
        results = {}
        
        # Testa cada arquivo
        for file_path in static_files:
            start_time = time.time()
            response = client.get(file_path)
            end_time = time.time()
            
            # Calcula o tempo de resposta em milissegundos
            response_time = (end_time - start_time) * 1000
            
            # Armazena os resultados
            results[file_path] = {
                'status_code': response.status_code,
                'response_time_ms': response_time,
                'content_length': len(response.data) if hasattr(response, 'data') else 0
            }
            
            # Verifica se a resposta foi bem-sucedida
            assert response.status_code == 200, f"Arquivo estático {file_path} retornou status {response.status_code}"
            
            # Verifica se o tempo de resposta está dentro de limites aceitáveis para arquivos estáticos
            assert response_time < 200, f"Tempo de resposta para arquivo {file_path} muito alto: {response_time:.2f}ms"
        
        # Imprime os resultados para análise
        print("\nTempos de resposta para arquivos estáticos:")
        for file_path, data in results.items():
            print(f"{file_path}: {data['response_time_ms']:.2f}ms ({data['content_length']} bytes)") 