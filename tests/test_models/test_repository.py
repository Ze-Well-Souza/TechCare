"""
Testes para o padrão Repository implementado na aplicação
"""
import pytest
import os
import json
import tempfile
import uuid
from datetime import datetime
from app.models.repository import Repository
from typing import Optional, List
from unittest.mock import MagicMock, patch

class TestModel:
    """Modelo de teste para o Repository"""
    def __init__(self, id=None, name=None, value=None, category=None):
        self.id = id or str(uuid.uuid4())
        self.name = name or "Test Model"
        self.value = value or 42
        self.category = category
        self.timestamp = datetime.now().isoformat()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'value': self.value,
            'category': self.category,
            'timestamp': self.timestamp
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            value=data.get('value'),
            category=data.get('category')
        )

class TestRepository(Repository):
    """Implementação de teste do Repository"""
    def __init__(self, storage_path=None):
        super().__init__(TestModel)
        self._storage_path = storage_path
        self._entities = {}
        
        if storage_path:
            os.makedirs(storage_path, exist_ok=True)
    
    def get_by_id(self, id: str) -> Optional[TestModel]:
        """Retorna uma entidade pelo ID"""
        # Tenta buscar da memória primeiro
        if id in self._entities:
            return self._entities[id]
        
        # Se não encontrou e temos armazenamento em disco, tenta carregar
        if self._storage_path and os.path.exists(os.path.join(self._storage_path, f"{id}.json")):
            return self._load_from_disk(id)
        
        return None
        
    def get_all(self) -> List[TestModel]:
        """Retorna todas as entidades"""
        return list(self._entities.values())
        
    def create(self, **kwargs) -> TestModel:
        """Cria uma nova entidade"""
        entity = TestModel(**kwargs)
        self._entities[entity.id] = entity
        
        # Se temos armazenamento em disco, salva
        if self._storage_path:
            self._save_to_disk(entity)
            
        return entity
        
    def update(self, id: str, **kwargs) -> TestModel:
        """Atualiza uma entidade existente"""
        entity = self.get_by_id(id)
        if not entity:
            raise ValueError(f"Entidade com ID {id} não encontrada")
            
        for key, value in kwargs.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
                
        # Se temos armazenamento em disco, atualiza
        if self._storage_path:
            self._save_to_disk(entity)
            
        return entity
        
    def delete(self, id: str) -> bool:
        """Remove uma entidade pelo ID"""
        if id in self._entities:
            del self._entities[id]
            
            # Se temos armazenamento em disco, remove o arquivo
            if self._storage_path:
                file_path = os.path.join(self._storage_path, f"{id}.json")
                if os.path.exists(file_path):
                    os.remove(file_path)
                    
            return True
            
        return False
        
    def find(self, **kwargs) -> List[TestModel]:
        """Busca entidades por critérios"""
        result = []
        
        for entity in self._entities.values():
            match = True
            for key, value in kwargs.items():
                if not hasattr(entity, key) or getattr(entity, key) != value:
                    match = False
                    break
            
            if match:
                result.append(entity)
                
        return result
        
    def _save_to_disk(self, entity: TestModel) -> None:
        """Salva uma entidade em disco"""
        if not self._storage_path:
            return
            
        file_path = os.path.join(self._storage_path, f"{entity.id}.json")
        with open(file_path, 'w') as f:
            json.dump(entity.to_dict(), f)
            
    def _load_from_disk(self, entity_id: str) -> Optional[TestModel]:
        """Carrega uma entidade do disco"""
        if not self._storage_path:
            return None
            
        file_path = os.path.join(self._storage_path, f"{entity_id}.json")
        if not os.path.exists(file_path):
            return None
            
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        entity = TestModel.from_dict(data)
        self._entities[entity.id] = entity
        return entity

@pytest.fixture
def temp_storage_path():
    """Cria um diretório temporário para armazenamento"""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname

def test_repository_initialization():
    """Testa a inicialização do repositório"""
    repo = TestRepository()
    assert repo.model_class == TestModel
    assert repo._storage_path is None
    assert isinstance(repo._entities, dict)
    assert len(repo._entities) == 0

def test_repository_with_storage_path(temp_storage_path):
    """Testa a inicialização do repositório com caminho de armazenamento"""
    repo = TestRepository(storage_path=temp_storage_path)
    assert repo._storage_path == temp_storage_path
    assert os.path.exists(temp_storage_path)

def test_repository_create():
    """Testa a criação de uma entidade no repositório"""
    repo = TestRepository()
    entity = repo.create(name="Test Entity", value=100)
    
    assert entity.id is not None
    assert entity.name == "Test Entity"
    assert entity.value == 100
    assert entity.id in repo._entities
    assert repo._entities[entity.id] is entity

def test_repository_get_by_id():
    """Testa a obtenção de uma entidade pelo ID"""
    repo = TestRepository()
    entity = repo.create(name="Test Entity", value=100)
    
    retrieved = repo.get_by_id(entity.id)
    assert retrieved is entity
    assert retrieved.name == "Test Entity"
    assert retrieved.value == 100
    
    # Testa ID inexistente
    assert repo.get_by_id("nonexistent") is None

def test_repository_get_all():
    """Testa a obtenção de todas as entidades"""
    repo = TestRepository()
    entity1 = repo.create(name="Entity 1", value=100)
    entity2 = repo.create(name="Entity 2", value=200)
    entity3 = repo.create(name="Entity 3", value=300)
    
    all_entities = repo.get_all()
    assert len(all_entities) == 3
    assert entity1 in all_entities
    assert entity2 in all_entities
    assert entity3 in all_entities

def test_repository_update():
    """Testa a atualização de uma entidade"""
    repo = TestRepository()
    entity = repo.create(name="Original Name", value=100)
    
    # Salva o ID para comparação posterior
    entity_id = entity.id
    
    # Atualiza a entidade
    updated = repo.update(entity_id, name="Updated Name", value=200)
    
    # Verifica se a entidade retornada foi atualizada
    assert updated.id == entity_id
    assert updated.name == "Updated Name"
    assert updated.value == 200
    
    # Verifica se a entidade no repositório também foi atualizada
    stored = repo.get_by_id(entity_id)
    assert stored.name == "Updated Name"
    assert stored.value == 200
    
    # Garante que é a mesma instância
    assert stored is entity

def test_repository_update_nonexistent():
    """Testa a atualização de uma entidade inexistente"""
    repo = TestRepository()
    
    # Tenta atualizar uma entidade que não existe
    with pytest.raises(ValueError, match="Entidade com ID .* não encontrada"):
        repo.update("nonexistent", name="Updated Name")

def test_repository_delete():
    """Testa a remoção de uma entidade"""
    repo = TestRepository()
    entity = repo.create(name="Entity to Delete")
    
    # Verifica que a entidade existe
    assert repo.get_by_id(entity.id) is not None
    
    # Remove a entidade
    result = repo.delete(entity.id)
    
    # Verifica que a operação foi bem sucedida
    assert result is True
    
    # Verifica que a entidade foi removida
    assert repo.get_by_id(entity.id) is None
    assert entity.id not in repo._entities

def test_repository_delete_nonexistent():
    """Testa a remoção de uma entidade inexistente"""
    repo = TestRepository()
    
    # Tenta remover uma entidade que não existe
    result = repo.delete("nonexistent")
    
    # Verifica que a operação falhou
    assert result is False

def test_repository_find():
    """Testa a busca de entidades por critérios"""
    repo = TestRepository()
    
    # Cria algumas entidades com diferentes valores
    repo.create(name="Entity 1", value=100)
    repo.create(name="Entity 2", value=200)
    repo.create(name="Entity 3", value=100)
    repo.create(name="Entity 4", value=300)
    
    # Busca entidades por valor
    found = repo.find(value=100)
    assert len(found) == 2
    assert all(entity.value == 100 for entity in found)
    
    # Busca entidades por nome
    found = repo.find(name="Entity 2")
    assert len(found) == 1
    assert found[0].name == "Entity 2"
    
    # Busca combinando critérios
    found = repo.find(name="Entity 3", value=100)
    assert len(found) == 1
    assert found[0].name == "Entity 3"
    assert found[0].value == 100
    
    # Busca sem resultados
    found = repo.find(name="Nonexistent")
    assert len(found) == 0

def test_repository_disk_storage():
    """Testa o armazenamento em disco"""
    # Cria um diretório temporário para o teste
    with tempfile.TemporaryDirectory() as temp_dir:
        # Cria um repositório com armazenamento em disco
        repo = TestRepository(storage_path=temp_dir)
        
        # Cria uma entidade
        entity = repo.create(name="Persisted Entity", value=123)
        entity_id = entity.id
        
        # Verifica se o arquivo foi criado
        file_path = os.path.join(temp_dir, f"{entity_id}.json")
        assert os.path.exists(file_path)
        
        # Cria um novo repositório apontando para o mesmo diretório
        repo2 = TestRepository(storage_path=temp_dir)
        
        # Verifica se é possível carregar a entidade do disco
        loaded = repo2.get_by_id(entity_id)
        assert loaded is not None
        assert loaded.id == entity_id
        assert loaded.name == "Persisted Entity"
        assert loaded.value == 123
        
        # Atualiza a entidade
        repo2.update(entity_id, name="Updated on Disk")
        
        # Verifica se o arquivo foi atualizado
        with open(file_path, 'r') as f:
            data = json.load(f)
            assert data['name'] == "Updated on Disk"
        
        # Remove a entidade
        repo2.delete(entity_id)
        
        # Verifica se o arquivo foi removido
        assert not os.path.exists(file_path)

def test_repository_complex_query():
    """Testa consultas mais complexas no repositório"""
    repo = TestRepository()
    
    # Cria várias entidades para teste
    for i in range(10):
        value = 100 if i < 5 else 200
        category = "A" if i % 2 == 0 else "B"
        repo.create(name=f"Entity {i}", value=value, category=category)
    
    # Implementa uma consulta personalizada
    def query_complex(repo):
        # Busca todas as entidades
        all_entities = repo.get_all()
        
        # Filtra manualmente (simulando uma consulta mais complexa)
        result = [
            entity for entity in all_entities
            if entity.value == 100 and entity.category == "A"
        ]
        
        return result
    
    # Executa a consulta
    result = query_complex(repo)
    
    # Verifica os resultados
    assert len(result) == 3  # Entidades 0, 2, 4 (valor=100, categoria=A)
    for entity in result:
        assert entity.value == 100
        assert entity.category == "A"

def test_delete_by_id_calls_delete(monkeypatch):
    repo = TestRepository()
    monkeypatch.setattr(repo, 'get_by_id', lambda id: 'obj' if id == 1 else None)
    monkeypatch.setattr(repo, 'delete', lambda obj: True)
    assert repo.delete_by_id(1) is True
    assert repo.delete_by_id(2) is False

def test_exists_calls_filter_by(monkeypatch):
    repo = TestRepository()
    class Query:
        def filter_by(self, **kwargs):
            class Q:
                def first(self):
                    return True
            return Q()
    repo.model_class = MagicMock()
    repo.model_class.query = Query()
    assert repo.exists(foo='bar') is True

def test_count_calls_query(monkeypatch):
    repo = TestRepository()
    class Query:
        def count(self):
            return 42
    repo.model_class = MagicMock()
    repo.model_class.query = Query()
    assert repo.count() == 42

def test_save_raises_on_sqlalchemy_error(monkeypatch):
    repo = TestRepository()
    class DummySession:
        def add(self, obj):
            raise Exception('fail')
        def commit(self):
            pass
        def rollback(self):
            self.rolled_back = True
    db = MagicMock()
    db.session = DummySession()
    monkeypatch.setattr('app.models.repository.db', db)
    with pytest.raises(Exception):
        repo.save('obj')

def test_delete_rollback_on_error(monkeypatch):
    repo = TestRepository()
    class DummySession:
        def delete(self, obj):
            raise Exception('fail')
        def commit(self):
            pass
        def rollback(self):
            self.rolled_back = True
    db = MagicMock()
    db.session = DummySession()
    monkeypatch.setattr('app.models.repository.db', db)
    assert repo.delete('obj') is False 