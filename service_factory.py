"""
Módulo que implementa o padrão Factory para criação de serviços.
"""
from typing import Dict, Type, Any, Optional

class ServiceFactory:
    """
    Fábrica para criação de serviços com injeção de dependências.
    Implementa o padrão Singleton para cada tipo de serviço.
    """
    
    _instances: Dict[str, Any] = {}
    _dependencies: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def register_dependency(cls, service_type: str, name: str, dependency: Any) -> None:
        """
        Registra uma dependência para um tipo de serviço
        
        Args:
            service_type: Tipo do serviço (nome da classe)
            name: Nome da dependência
            dependency: Objeto de dependência
        """
        if service_type not in cls._dependencies:
            cls._dependencies[service_type] = {}
            
        cls._dependencies[service_type][name] = dependency
        
        # Se o serviço já foi instanciado, recria-o com as novas dependências
        if service_type in cls._instances:
            del cls._instances[service_type]
    
    @classmethod
    def get_service(cls, service_class: Type) -> Any:
        """
        Obtém uma instância do serviço, criando-a se necessário
        
        Args:
            service_class: Classe do serviço a ser criado/obtido
            
        Returns:
            Instância do serviço solicitado
        """
        service_type = service_class.__name__
        
        # Se já existe uma instância, retorna-a
        if service_type in cls._instances:
            return cls._instances[service_type]
        
        # Obtém as dependências registradas para este tipo de serviço
        dependencies = cls._dependencies.get(service_type, {})
        
        # Cria uma nova instância com as dependências
        instance = service_class(**dependencies)
        cls._instances[service_type] = instance
        return instance
    
    @classmethod
    def clear_instance(cls, service_type: str) -> None:
        """
        Remove uma instância do cache de serviços
        
        Args:
            service_type: Tipo do serviço a ser removido
        """
        if service_type in cls._instances:
            del cls._instances[service_type]
    
    @classmethod
    def clear_all(cls) -> None:
        """
        Limpa todas as instâncias de serviços
        """
        cls._instances.clear() 