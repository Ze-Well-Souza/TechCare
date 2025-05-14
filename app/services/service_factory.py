"""
Módulo que implementa o padrão Factory para criação de serviços.
"""
from typing import Dict, Type, Any, Optional
import logging
import sys

from app.services.diagnostic_service import DiagnosticService
from app.services.cleaner_service import CleanerService
from app.services.repair_service import RepairService
from app.services.driver_update_service import DriverUpdateService
from app.services.diagnostic_repository import DiagnosticRepository
from app.services.visualization_service import VisualizationService

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

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

    def __init__(self):
        """Inicializa a fábrica de serviços"""
        logger.info("Inicializando ServiceFactory")
        # Instanciando repositórios compartilhados
        self.diagnostic_repository = DiagnosticRepository()
        
    def create_diagnostic_service(self) -> DiagnosticService:
        """
        Cria uma instância do serviço de diagnóstico com suas dependências
        
        Returns:
            DiagnosticService: Instância configurada do serviço
        """
        logger.info("Criando instância de DiagnosticService")
        return DiagnosticService(diagnostic_repository=self.diagnostic_repository)
    
    def create_cleaner_service(self) -> CleanerService:
        """
        Cria uma instância do serviço de limpeza
        
        Returns:
            CleanerService: Instância configurada do serviço
        """
        logger.info("Criando instância de CleanerService")
        return CleanerService()
    
    def create_repair_service(self) -> RepairService:
        """
        Cria uma instância do serviço de reparo
        
        Returns:
            RepairService: Instância configurada do serviço
        """
        logger.info("Criando instância de RepairService")
        return RepairService()
    
    def create_driver_update_service(self) -> DriverUpdateService:
        """
        Cria uma instância do serviço de atualização de drivers
        
        Returns:
            DriverUpdateService: Instância configurada do serviço
        """
        logger.info("Criando instância de DriverUpdateService")
        return DriverUpdateService()
    
    def create_visualization_service(self) -> VisualizationService:
        """
        Cria uma instância do serviço de visualização com suas dependências
        
        Returns:
            VisualizationService: Instância configurada do serviço
        """
        logger.info("Criando instância de VisualizationService")
        return VisualizationService(diagnostic_repository=self.diagnostic_repository) 