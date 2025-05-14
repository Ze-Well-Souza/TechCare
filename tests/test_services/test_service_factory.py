"""
Testes para o ServiceFactory.
"""
import pytest
from app.services.service_factory import ServiceFactory

# Classe mock para testar a factory
class MockService:
    def __init__(self, **kwargs):
        self.dependencies = kwargs
        
    def get_dependency(self, name):
        return self.dependencies.get(name)

class TestServiceFactory:
    """
    Testes para o ServiceFactory que implementa o padrão Factory
    para injeção de dependências e singleton.
    """
    
    def setup_method(self):
        """Configuração antes de cada teste"""
        # Limpa todas as instâncias e dependências
        ServiceFactory._instances = {}
        ServiceFactory._dependencies = {}
    
    def test_get_service_creates_new_instance(self):
        """Testa se o factory cria uma nova instância de serviço"""
        service = ServiceFactory.get_service(MockService)
        
        # Verifica se o serviço foi criado corretamente
        assert service is not None
        assert isinstance(service, MockService)
        
        # Verifica se a instância está no cache
        assert 'MockService' in ServiceFactory._instances
        assert ServiceFactory._instances['MockService'] is service
    
    def test_get_service_returns_same_instance(self):
        """Testa se o factory retorna a mesma instância na segunda chamada (singleton)"""
        service1 = ServiceFactory.get_service(MockService)
        service2 = ServiceFactory.get_service(MockService)
        
        # Verifica se são o mesmo objeto (singleton)
        assert service1 is service2
    
    def test_register_dependency(self):
        """Testa o registro de dependências"""
        # Registra dependências
        ServiceFactory.register_dependency('MockService', 'config', {'timeout': 30})
        ServiceFactory.register_dependency('MockService', 'logger', 'mock_logger')
        
        # Cria o serviço com as dependências
        service = ServiceFactory.get_service(MockService)
        
        # Verifica se as dependências foram injetadas
        assert service.get_dependency('config') == {'timeout': 30}
        assert service.get_dependency('logger') == 'mock_logger'
    
    def test_register_dependency_recreates_instance(self):
        """Testa se o registro de dependências recria instâncias existentes"""
        # Cria uma instância inicial
        service1 = ServiceFactory.get_service(MockService)
        
        # Registra uma nova dependência
        ServiceFactory.register_dependency('MockService', 'new_dep', 'value')
        
        # Obtém o serviço novamente
        service2 = ServiceFactory.get_service(MockService)
        
        # Verifica que uma nova instância foi criada
        assert service1 is not service2
        assert service2.get_dependency('new_dep') == 'value'
    
    def test_clear_instance(self):
        """Testa a limpeza de instâncias específicas"""
        # Cria uma instância
        service = ServiceFactory.get_service(MockService)
        assert 'MockService' in ServiceFactory._instances
        
        # Limpa a instância
        ServiceFactory.clear_instance('MockService')
        assert 'MockService' not in ServiceFactory._instances
        
        # Cria uma nova instância e verifica que é diferente
        new_service = ServiceFactory.get_service(MockService)
        assert new_service is not service
    
    def test_clear_all(self):
        """Testa a limpeza de todas as instâncias"""
        # Cria várias instâncias de classes diferentes
        class AnotherMockService:
            pass
            
        service1 = ServiceFactory.get_service(MockService)
        service2 = ServiceFactory.get_service(AnotherMockService)
        
        assert 'MockService' in ServiceFactory._instances
        assert 'AnotherMockService' in ServiceFactory._instances
        
        # Limpa todas as instâncias
        ServiceFactory.clear_all()
        
        assert len(ServiceFactory._instances) == 0
        
        # Cria novas instâncias e verifica que são diferentes
        new_service1 = ServiceFactory.get_service(MockService)
        new_service2 = ServiceFactory.get_service(AnotherMockService)
        
        assert new_service1 is not service1
        assert new_service2 is not service2 