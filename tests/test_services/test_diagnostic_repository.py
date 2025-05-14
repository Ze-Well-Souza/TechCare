"""
Testes para o DiagnosticRepository.
"""
import pytest
import os
import json
import tempfile
import datetime
from pathlib import Path
from app.services.diagnostic_repository import DiagnosticRepository
from collections import defaultdict
import shutil


class TestDiagnosticRepository:
    """
    Testes para o DiagnosticRepository que implementa o padrão Repository
    para persistência e recuperação de diagnósticos.
    """
    
    def setup_method(self, method):
        """Configura o ambiente para os testes"""
        self.test_dir = tempfile.mkdtemp()
        self.repository = DiagnosticRepository(self.test_dir)
        # Limpa completamente o repositório para os testes
        self.repository._diagnostics.clear()
        
        # Diagnóstico de exemplo para testes
        self.sample_diagnostic = {
            'id': 'diag-04183921',
            'user_id': 'user1',  # Alterando para 'user1' para consistência com os testes
            'score': 85,
            'timestamp': '2023-01-01T12:00:00',
            'components': {
                'cpu': {'status': 'good', 'score': 90},
                'memory': {'status': 'warning', 'score': 70},
                'disk': {'status': 'good', 'score': 95},
                'network': {'status': 'good', 'score': 85}
            }
        }
    
    def teardown_method(self, method):
        """Limpa o ambiente após cada teste"""
        # Remove o diretório temporário
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
        # Garante que o repositório seja limpo
        self.repository._diagnostics.clear()
    
    def test_repository_initialization(self):
        """Testa a inicialização do repositório"""
        # Verifica se o repositório foi inicializado corretamente
        assert self.repository.storage_path == self.test_dir
        assert isinstance(self.repository._diagnostics, dict)
        
        # Verifica se o diretório de armazenamento foi criado
        storage_dir = Path(self.test_dir)
        assert storage_dir.exists()
        assert storage_dir.is_dir()
    
    def test_save_diagnostic(self):
        """Testa o salvamento de um diagnóstico"""
        # Salva um diagnóstico
        diagnostic_id = self.repository.save(self.sample_diagnostic)
        
        # Verifica se o ID foi gerado
        assert diagnostic_id is not None
        assert diagnostic_id.startswith('diag-')
        
        # Verifica se o diagnóstico foi armazenado em memória
        user_id = self.sample_diagnostic['user_id']
        assert user_id in self.repository._diagnostics
        assert len(self.repository._diagnostics[user_id]) == 1
        assert self.repository._diagnostics[user_id][0]['id'] == diagnostic_id
        
        # Verifica se foi salvo em disco
        user_dir = Path(self.test_dir) / user_id
        assert user_dir.exists()
        
        file_path = user_dir / f"{diagnostic_id}.json"
        assert file_path.exists()
        
        # Verifica o conteúdo do arquivo
        with open(file_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
            
        assert saved_data['id'] == diagnostic_id
        assert saved_data['user_id'] == user_id
        assert saved_data['score'] == 85
    
    def test_save_diagnostic_with_existing_id(self):
        """Testa o salvamento de um diagnóstico com ID existente"""
        # Cria um diagnóstico com ID predefinido
        diagnostic_with_id = self.sample_diagnostic.copy()
        diagnostic_with_id['id'] = 'diag-test-123'
        
        # Salva o diagnóstico
        diagnostic_id = self.repository.save(diagnostic_with_id)
        
        # Verifica se o ID foi mantido
        assert diagnostic_id == 'diag-test-123'
        
        # Verifica se foi salvo corretamente
        saved_diagnostic = self.repository.get_by_id('diag-test-123', 'user1')
        assert saved_diagnostic is not None
        assert saved_diagnostic['id'] == 'diag-test-123'
    
    def test_get_by_id_found_in_memory(self):
        """Testa a recuperação de um diagnóstico pelo ID quando está em memória"""
        # Salva um diagnóstico
        diagnostic_id = self.repository.save(self.sample_diagnostic)
        
        # Recupera o diagnóstico
        diagnostic = self.repository.get_by_id(diagnostic_id, 'user1')
        
        # Verifica se foi encontrado e está correto
        assert diagnostic is not None
        assert diagnostic['id'] == diagnostic_id
        assert diagnostic['user_id'] == 'user1'
        assert diagnostic['score'] == 85
    
    def test_get_by_id_found_on_disk(self):
        """Testa a recuperação de um diagnóstico pelo ID quando está apenas em disco"""
        # Salva um diagnóstico
        diagnostic_id = self.repository.save(self.sample_diagnostic)
        
        # Limpa o cache em memória
        self.repository._diagnostics = {}
        
        # Recupera o diagnóstico
        diagnostic = self.repository.get_by_id(diagnostic_id, 'user1')
        
        # Verifica se foi encontrado e está correto
        assert diagnostic is not None
        assert diagnostic['id'] == diagnostic_id
        assert diagnostic['user_id'] == 'user1'
        assert diagnostic['score'] == 85
    
    def test_get_by_id_not_found(self):
        """Testa a tentativa de recuperação de um diagnóstico inexistente"""
        # Tenta recuperar um diagnóstico inexistente
        diagnostic = self.repository.get_by_id('diag-nonexistent', 'user1')
        
        # Verifica que não foi encontrado
        assert diagnostic is None
    
    def test_get_by_id_any_user(self):
        """Testa a recuperação de um diagnóstico sem especificar o usuário"""
        # Salva diagnósticos para diferentes usuários e adiciona um atraso para garantir timestamps diferentes
        diagnostic1 = self.sample_diagnostic.copy()
        diagnostic1['id'] = 'diag-test-user1'
        diagnostic1['user_id'] = 'user1'
        self.repository.save(diagnostic1)
        
        diagnostic2 = self.sample_diagnostic.copy()
        diagnostic2['id'] = 'diag-test-user2'
        diagnostic2['user_id'] = 'user2'
        self.repository.save(diagnostic2)
        
        # Recupera sem especificar o usuário
        found_diagnostic1 = self.repository.get_by_id('diag-test-user1')
        found_diagnostic2 = self.repository.get_by_id('diag-test-user2')
        
        # Verifica se encontrou ambos
        assert found_diagnostic1 is not None
        assert found_diagnostic1['id'] == 'diag-test-user1'
        assert found_diagnostic1['user_id'] == 'user1'
        
        assert found_diagnostic2 is not None
        assert found_diagnostic2['id'] == 'diag-test-user2'
        assert found_diagnostic2['user_id'] == 'user2'
    
    def test_get_history(self):
        """Testa a recuperação do histórico de diagnósticos de um usuário"""
        # Salva múltiplos diagnósticos para um usuário
        for i in range(5):
            diagnostic = self.sample_diagnostic.copy()
            diagnostic['score'] = 80 + i  # Variar um pouco os dados
            self.repository.save(diagnostic)
        
        # Recupera o histórico
        history = self.repository.get_history('user1', limit=3)
        
        # Verifica se recuperou os registros mais recentes
        assert len(history) == 3
        
        # Verifica se estão ordenados por timestamp (mais recente primeiro)
        timestamps = [item.get('timestamp', '') for item in history]
        assert timestamps[0] >= timestamps[1] >= timestamps[2]
    
    def test_get_history_from_disk(self):
        """Testa a recuperação do histórico de diagnósticos do disco"""
        # Salva alguns diagnósticos com IDs e timestamps diferentes
        for i in range(3):
            diagnostic = self.sample_diagnostic.copy()
            diagnostic['id'] = f'diag-test-history-{i}'
            diagnostic['timestamp'] = f'2023-01-{i+1:02d}T12:00:00'  # Timestamps diferentes
            diagnostic['score'] = 80 + i
            self.repository.save(diagnostic)
        
        # Limpa o cache em memória para forçar a leitura do disco
        self.repository._diagnostics = {}
        
        # Recupera o histórico
        history = self.repository.get_history('user1')
        
        # Verifica se recuperou os registros do disco
        assert len(history) == 3
        # Verifica se estão ordenados por timestamp (mais recente primeiro)
        assert history[0]['id'] == 'diag-test-history-2'  # O registro com data mais recente vem primeiro
        assert history[2]['id'] == 'diag-test-history-0'  # O registro com data mais antiga vem por último
    
    def test_get_all(self):
        """Testa a recuperação de todos os diagnósticos"""
        # Limpa o dicionário de diagnósticos para ter um estado limpo
        # Usar defaultdict para evitar o KeyError
        self.repository._diagnostics = defaultdict(list)
        
        # Salva diagnósticos para diferentes usuários
        diagnostic1 = self.sample_diagnostic.copy()
        diagnostic1['user_id'] = 'user1'
        self.repository.save(diagnostic1)
        
        diagnostic2 = self.sample_diagnostic.copy()
        diagnostic2['user_id'] = 'user2'
        self.repository.save(diagnostic2)
        
        # Recupera todos os diagnósticos
        all_diagnostics = self.repository.get_all()
        
        # Verifica se recuperou todos
        assert len(all_diagnostics) == 2
        
        # Verifica se contém diagnósticos dos dois usuários
        user_ids = [d.get('user_id') for d in all_diagnostics]
        assert 'user1' in user_ids
        assert 'user2' in user_ids
    
    def test_get_count(self):
        """Testa a contagem de diagnósticos"""
        # Verifica a contagem inicial
        initial_count = self.repository.get_count()
        assert initial_count == 0
        
        # Salva alguns diagnósticos
        for i in range(3):
            diagnostic = self.sample_diagnostic.copy()
            self.repository.save(diagnostic)
        
        # Verifica a nova contagem
        new_count = self.repository.get_count()
        assert new_count == 3
        
        # Verifica a contagem para um usuário específico
        user_count = self.repository.get_count('user1')
        assert user_count == 3
        
        # Verifica a contagem para um usuário sem diagnósticos
        empty_count = self.repository.get_count('nonexistent')
        assert empty_count == 0
    
    def test_timestamp_added_when_missing(self):
        """Testa se o timestamp é adicionado automaticamente quando ausente"""
        # Cria um diagnóstico sem timestamp
        diagnostic_without_timestamp = self.sample_diagnostic.copy()
        if 'timestamp' in diagnostic_without_timestamp:
            del diagnostic_without_timestamp['timestamp']
        
        # Salva o diagnóstico
        diagnostic_id = self.repository.save(diagnostic_without_timestamp)
        
        # Recupera o diagnóstico
        diagnostic = self.repository.get_by_id(diagnostic_id)
        
        # Verifica se o timestamp foi adicionado
        assert 'timestamp' in diagnostic
        
        # Verifica se é um timestamp válido ISO 8601
        timestamp = diagnostic['timestamp']
        try:
            datetime.datetime.fromisoformat(timestamp)
            is_valid = True
        except ValueError:
            is_valid = False
            
        assert is_valid == True
    
    def test_disk_storage_error_handling(self):
        """Testa o tratamento de erro ao salvar em disco"""
        # Cria um repositório com um caminho inválido
        invalid_path = "/path/that/should/not/exist/12345"
        repo_with_invalid_path = DiagnosticRepository(storage_path=invalid_path)
        
        # Tenta salvar um diagnóstico
        # Não deve lançar exceção, apenas logar o erro
        diagnostic_id = repo_with_invalid_path.save(self.sample_diagnostic)
        
        # Verifica se foi salvo em memória
        user_id = self.sample_diagnostic['user_id']
        assert user_id in repo_with_invalid_path._diagnostics
        assert len(repo_with_invalid_path._diagnostics[user_id]) == 1
        assert repo_with_invalid_path._diagnostics[user_id][0]['id'] == diagnostic_id 