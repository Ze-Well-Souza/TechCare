"""
Módulo para implementação de cache em memória para otimizar operações frequentes.
"""
from functools import wraps
from datetime import datetime, timedelta
import threading
import hashlib
import json
import pickle
from typing import Any, Dict, Callable, Tuple, Union, Optional, List
import time

# Cache em memória global
_cache: Dict[str, Tuple[Any, datetime]] = {}
_cache_lock = threading.RLock()

class CacheItem:
    """
    Item de cache com tempo de expiração
    """
    def __init__(self, value: Any, ttl: float):
        """
        Inicializa um item de cache
        
        Args:
            value: Valor a ser armazenado
            ttl: Tempo de vida do item em segundos
        """
        self.value = value
        self.ttl = ttl
        self.created_at = time.time()
    
    def is_expired(self) -> bool:
        """
        Verifica se o item expirou
        
        Returns:
            True se o item expirou, False caso contrário
        """
        return time.time() > (self.created_at + self.ttl)


class Cache:
    """
    Implementação de cache em memória
    """
    def __init__(self, default_ttl: float = 300):
        """
        Inicializa um cache
        
        Args:
            default_ttl: Tempo de vida padrão em segundos (5 minutos)
        """
        self._cache: Dict[str, CacheItem] = {}
        self.default_ttl = default_ttl
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """
        Define um valor no cache
        
        Args:
            key: Chave para armazenar o valor
            value: Valor a ser armazenado
            ttl: Tempo de vida em segundos (usa o padrão se None)
        """
        ttl = ttl if ttl is not None else self.default_ttl
        self._cache[key] = CacheItem(value, ttl)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtém um valor do cache
        
        Args:
            key: Chave para buscar
            default: Valor padrão a retornar se a chave não existir
            
        Returns:
            Valor armazenado ou o valor padrão
        """
        if key in self._cache:
            cache_item = self._cache[key]
            if not cache_item.is_expired():
                return cache_item.value
            else:
                # Remove o item expirado
                del self._cache[key]
        
        return default
    
    def delete(self, key: str) -> None:
        """
        Remove um item do cache
        
        Args:
            key: Chave a ser removida
        """
        if key in self._cache:
            del self._cache[key]
    
    def clear(self) -> None:
        """
        Limpa todo o cache
        """
        self._cache.clear()
    
    def has_key(self, key: str) -> bool:
        """
        Verifica se uma chave existe no cache e não expirou
        
        Args:
            key: Chave a verificar
            
        Returns:
            True se a chave existir e não tiver expirado, False caso contrário
        """
        if key in self._cache:
            cache_item = self._cache[key]
            if not cache_item.is_expired():
                return True
            else:
                # Remove o item expirado
                del self._cache[key]
        
        return False


# Cache global para uso com o decorador
_global_cache = Cache()

def _get_cache_key(func_name: str, args: Tuple, kwargs: Dict) -> str:
    """
    Gera uma chave única para o cache baseado na função e seus argumentos
    
    Args:
        func_name: Nome da função
        args: Argumentos posicionais
        kwargs: Argumentos nomeados
        
    Returns:
        Chave de hash para o cache
    """
    # Concatena o nome da função com a representação dos argumentos
    key_data = {
        'func': func_name,
        'args': args,
        'kwargs': sorted(kwargs.items())  # Ordenar para garantir consistência
    }
    
    try:
        # Tenta usar json para serializar (mais rápido)
        key_str = json.dumps(key_data, sort_keys=True)
    except (TypeError, ValueError):
        # Fallback para representação como string se não for serializável
        key_str = str(key_data)
    
    # Gera um hash MD5 da representação
    return hashlib.md5(key_str.encode('utf-8')).hexdigest()

def cached(ttl: float = None, expire_seconds: float = None):
    """
    Decorador para cache de resultados de funções.
    
    Args:
        ttl: Tempo de vida em segundos (usa o padrão do cache se None)
        expire_seconds: Alias para ttl para compatibilidade com código existente
        
    Returns:
        Decorador de função
    """
    # Usa expire_seconds se ttl não for fornecido (para compatibilidade)
    if ttl is None and expire_seconds is not None:
        ttl = expire_seconds
        
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gera a chave do cache
            cache_key = _get_cache_key(func.__name__, args, kwargs)
            
            # Verifica se o resultado está em cache
            result = _global_cache.get(cache_key)
            if result is not None:
                return result
            
            # Executa a função original
            result = func(*args, **kwargs)
            
            # Armazena o resultado em cache
            _global_cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# Para manter compatibilidade com código existente
cache_result = cached

def invalidate_cache(func_name: Optional[str] = None) -> int:
    """
    Invalida entradas de cache específicas ou todo o cache
    
    Args:
        func_name: Nome da função para invalidar (None para invalidar tudo)
        
    Returns:
        Número de entradas de cache invalidadas
    """
    if func_name is None:
        # Invalida todo o cache
        count = len(_global_cache._cache)
        _global_cache.clear()
        return count
    
    # Invalida apenas entradas relacionadas à função especificada
    keys_to_remove = [k for k in _global_cache._cache.keys() if k.startswith(func_name)]
    for k in keys_to_remove:
        _global_cache.delete(k)
    
    return len(keys_to_remove)

def get_cache_stats() -> Dict[str, int]:
    """
    Retorna estatísticas sobre o cache
    
    Returns:
        Dicionário com estatísticas do cache
    """
    total = len(_global_cache._cache)
    expired = sum(1 for item in _global_cache._cache.values() if item.is_expired())
    valid = total - expired
    
    return {
        'total_entries': total,
        'valid_entries': valid,
        'expired_entries': expired
    } 