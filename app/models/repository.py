"""
Módulo que implementa o padrão Repository para modelos de dados.
Este padrão separa a lógica de acesso a dados da lógica de negócio,
facilitando testes, manutenção e extensibilidade.
"""
from typing import TypeVar, Generic, Type, List, Optional, Any, Dict, Union
from sqlalchemy.exc import SQLAlchemyError
from app import db

T = TypeVar('T')

class Repository(Generic[T]):
    """
    Classe genérica de repositório para acesso a dados.
    Implementa operações CRUD básicas para qualquer modelo.
    """
    def __init__(self, model_class: Type[T]):
        self.model_class = model_class

    def get_by_id(self, id: int) -> Optional[T]:
        """Retorna um objeto pelo seu ID"""
        return db.session.get(self.model_class, id)

    def get_all(self) -> List[T]:
        """Retorna todos os objetos do modelo"""
        return self.model_class.query.all()

    def filter_by(self, **kwargs) -> List[T]:
        """Filtra objetos por atributos específicos"""
        return self.model_class.query.filter_by(**kwargs).all()

    def get_one_by(self, **kwargs) -> Optional[T]:
        """Retorna um único objeto que atende aos critérios"""
        return self.model_class.query.filter_by(**kwargs).first()

    def create(self, **kwargs) -> T:
        """Cria um novo objeto no banco de dados"""
        obj = self.model_class(**kwargs)
        return self.save(obj)

    def update(self, obj: T, **kwargs) -> T:
        """Atualiza um objeto existente"""
        for key, value in kwargs.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return self.save(obj)

    def save(self, obj: T) -> T:
        """Salva um objeto no banco de dados"""
        try:
            db.session.add(obj)
            db.session.commit()
            return obj
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    def delete(self, obj: T) -> bool:
        """Remove um objeto do banco de dados"""
        try:
            db.session.delete(obj)
            db.session.commit()
            return True
        except SQLAlchemyError:
            db.session.rollback()
            return False

    def delete_by_id(self, id: int) -> bool:
        """Remove um objeto pelo seu ID"""
        obj = self.get_by_id(id)
        if obj:
            return self.delete(obj)
        return False

    def count(self) -> int:
        """Conta o número total de registros"""
        return self.model_class.query.count()

    def exists(self, **kwargs) -> bool:
        """Verifica se existe algum registro com os critérios fornecidos"""
        return self.model_class.query.filter_by(**kwargs).first() is not None 