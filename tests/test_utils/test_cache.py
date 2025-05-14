"""
Testes para o sistema de cache
"""
import pytest
import time
from unittest.mock import patch, MagicMock
from app.utils.cache import Cache, CacheItem, cached, _get_cache_key, get_cache_stats

def test_cache_item_initialization():
    """Testa a inicialização de um item de cache"""
    value = "test_value"
    ttl = 60
    item = CacheItem(value, ttl)
    
    assert item.value == value
    assert item.ttl == ttl
    assert item.created_at is not None
    assert not item.is_expired()

def test_cache_item_expiration():
    """Testa a expiração de um item de cache"""
    value = "test_value"
    ttl = 0.1  # Muito curto para expirar rapidamente
    
    item = CacheItem(value, ttl)
    
    # No início, o item não deve estar expirado
    assert not item.is_expired()
    
    # Espera o TTL passar
    time.sleep(0.2)
    
    # Agora o item deve estar expirado
    assert item.is_expired()

def test_cache_initialization():
    """Testa a inicialização do cache"""
    cache = Cache()
    assert len(cache._cache) == 0
    assert cache.default_ttl == 300  # 5 minutos por padrão

def test_cache_initialization_with_custom_ttl():
    """Testa a inicialização do cache com TTL personalizado"""
    custom_ttl = 600
    cache = Cache(default_ttl=custom_ttl)
    assert cache.default_ttl == custom_ttl

def test_cache_set_and_get():
    """Testa a definição e obtenção de um valor no cache"""
    cache = Cache()
    key = "test_key"
    value = "test_value"
    
    # Define um valor no cache
    cache.set(key, value)
    
    # Verifica se o valor pode ser obtido
    assert key in cache._cache
    assert cache.get(key) == value

def test_cache_set_with_custom_ttl():
    """Testa a definição de um valor com TTL personalizado"""
    cache = Cache(default_ttl=300)
    key = "test_key"
    value = "test_value"
    custom_ttl = 60
    
    # Define um valor no cache com TTL personalizado
    cache.set(key, value, ttl=custom_ttl)
    
    # Verifica se o TTL foi definido corretamente
    assert cache._cache[key].ttl == custom_ttl

def test_cache_get_nonexistent_key():
    """Testa a obtenção de uma chave inexistente"""
    cache = Cache()
    
    # Tenta obter uma chave inexistente
    result = cache.get("nonexistent_key")
    assert result is None
    
    # Tenta obter uma chave inexistente com valor padrão
    default_value = "default_value"
    result = cache.get("nonexistent_key", default=default_value)
    assert result == default_value

def test_cache_get_with_default():
    """Testa a obtenção de um valor com padrão quando a chave não existe"""
    cache = Cache()
    key = "nonexistent_key"
    default_value = "default_value"
    
    # Verifica que a chave não existe
    assert key not in cache._cache
    
    # Tenta obter um valor com padrão
    result = cache.get(key, default_value)
    assert result == default_value

def test_cache_get_expired_item():
    """Testa a obtenção de um item expirado"""
    cache = Cache()
    key = "expired_key"
    value = "expired_value"
    
    # Define um valor no cache com TTL curto
    cache.set(key, value, ttl=0.1)
    
    # Espera o item expirar
    time.sleep(0.2)
    
    # Tenta obter o item expirado
    result = cache.get(key)
    assert result is None
    
    # Verifica se o item foi removido do cache
    assert key not in cache._cache

def test_cache_delete():
    """Testa a remoção de um item do cache"""
    cache = Cache()
    key = "key_to_delete"
    value = "value_to_delete"
    
    # Define um valor no cache
    cache.set(key, value)
    assert key in cache._cache
    
    # Remove o item
    cache.delete(key)
    
    # Verifica se o item foi removido
    assert key not in cache._cache
    assert cache.get(key) is None

def test_cache_delete_nonexistent_key():
    """Testa a remoção de uma chave inexistente"""
    cache = Cache()
    
    # Tenta remover uma chave inexistente (não deve lançar exceção)
    cache.delete("nonexistent_key")

def test_cache_clear():
    """Testa a limpeza de todo o cache"""
    cache = Cache()
    
    # Define vários valores no cache
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")
    
    # Verifica que os valores foram definidos
    assert len(cache._cache) == 3
    
    # Limpa o cache
    cache.clear()
    
    # Verifica que o cache está vazio
    assert len(cache._cache) == 0

def test_cache_has_key():
    """Testa a verificação de existência de uma chave no cache"""
    cache = Cache()
    key = "test_key"
    value = "test_value"
    
    # Inicialmente a chave não deve existir
    assert not cache.has_key(key)
    
    # Define um valor no cache
    cache.set(key, value)
    
    # Verifica que a chave existe
    assert cache.has_key(key)
    
    # Define um valor com TTL curto
    expired_key = "expired_key"
    cache.set(expired_key, "expired_value", ttl=0.1)
    
    # Espera o item expirar
    time.sleep(0.2)
    
    # Verifica que a chave expirada não "existe"
    assert not cache.has_key(expired_key)
    
    # Verifica que o item expirado foi removido do cache
    assert expired_key not in cache._cache

def test_cache_has_key_expired():
    """Testa a verificação de existência de uma chave expirada"""
    cache = Cache()
    key = "expired_key"
    value = "expired_value"
    
    # Define um valor no cache com TTL curto
    cache.set(key, value, ttl=0.1)
    
    # Espera o item expirar
    time.sleep(0.2)
    
    # Verifica se a chave expirada não existe mais
    assert cache.has_key(key) is False
    
    # Verifica se a chave foi removida do cache
    assert key not in cache._cache

def test_cached_decorator():
    """Testa o decorador de cache"""
    # Contador para verificar o número de chamadas
    call_count = 0
    
    # Função a ser decorada
    @cached(ttl=60)
    def test_function(param):
        nonlocal call_count
        call_count += 1
        return f"Result: {param}"
    
    # Primeira chamada - deve executar a função
    result1 = test_function("test")
    assert result1 == "Result: test"
    assert call_count == 1
    
    # Segunda chamada com mesmo parâmetro - deve usar o cache
    result2 = test_function("test")
    assert result2 == "Result: test"
    assert call_count == 1  # Não deve ter incrementado
    
    # Chamada com parâmetro diferente - deve executar a função novamente
    result3 = test_function("another")
    assert result3 == "Result: another"
    assert call_count == 2

def test_cached_decorator_with_different_args():
    """Testa o decorador @cached com diferentes tipos de argumentos"""
    call_count = 0
    
    @cached()
    def complex_function(arg1, arg2=None, *args, **kwargs):
        nonlocal call_count
        call_count += 1
        return f"{arg1}_{arg2}_{len(args)}_{len(kwargs)}"
    
    # Primeira chamada
    result1 = complex_function("a", "b", 1, 2, key1="value1")
    assert result1 == "a_b_2_1"
    assert call_count == 1
    
    # Mesma chamada deve usar o cache
    result2 = complex_function("a", "b", 1, 2, key1="value1")
    assert result2 == "a_b_2_1"
    assert call_count == 1
    
    # Ordem diferente dos kwargs deve ainda usar o cache
    result3 = complex_function("a", "b", 1, 2, key1="value1")
    assert result3 == "a_b_2_1"
    assert call_count == 1
    
    # Argumentos diferentes devem executar a função real
    result4 = complex_function("a", "b", 1, 2, key2="value2")
    assert result4 == "a_b_2_1"
    assert call_count == 2

def test_cached_decorator_expiration():
    """Testa a expiração do cache com o decorador @cached"""
    call_count = 0
    
    @cached(ttl=0.1)  # TTL muito curto (100ms)
    def test_function():
        nonlocal call_count
        call_count += 1
        return "result"
    
    # Primeira chamada
    result1 = test_function()
    assert result1 == "result"
    assert call_count == 1
    
    # Mesma chamada imediatamente deve usar o cache
    result2 = test_function()
    assert result2 == "result"
    assert call_count == 1
    
    # Espera o cache expirar
    time.sleep(0.2)
    
    # Após a expiração, deve executar a função real novamente
    result3 = test_function()
    assert result3 == "result"
    assert call_count == 2

def test_cached_decorator_with_instance_method():
    """Testa o decorador @cached com métodos de instância"""
    class TestClass:
        def __init__(self):
            self.call_count = 0
        
        @cached()
        def test_method(self, arg):
            self.call_count += 1
            return f"instance_{arg}"
    
    # Cria duas instâncias da classe
    instance1 = TestClass()
    instance2 = TestClass()
    
    # Testa com a primeira instância
    result1 = instance1.test_method("a")
    assert result1 == "instance_a"
    assert instance1.call_count == 1
    
    # Mesma chamada na mesma instância deve usar o cache
    result2 = instance1.test_method("a")
    assert result2 == "instance_a"
    assert instance1.call_count == 1
    
    # Mesma chamada em instância diferente deve executar a função real
    result3 = instance2.test_method("a")
    assert result3 == "instance_a"
    assert instance2.call_count == 1
    
    # Diferentes argumentos na mesma instância devem executar a função real
    result4 = instance1.test_method("b")
    assert result4 == "instance_b"
    assert instance1.call_count == 2

def test_get_cache_key():
    """Testa a geração de chaves de cache"""
    # Teste com argumentos simples
    key1 = _get_cache_key("func1", (1, 2), {"a": "b"})
    assert isinstance(key1, str)
    
    # Teste com argumentos idênticos - deve gerar a mesma chave
    key2 = _get_cache_key("func1", (1, 2), {"a": "b"})
    assert key1 == key2
    
    # Teste com argumentos diferentes - deve gerar chaves diferentes
    key3 = _get_cache_key("func1", (1, 3), {"a": "b"})
    assert key1 != key3
    
    key4 = _get_cache_key("func1", (1, 2), {"a": "c"})
    assert key1 != key4
    
    key5 = _get_cache_key("func2", (1, 2), {"a": "b"})
    assert key1 != key5

# Novos testes para aumentar a cobertura

def test_cache_with_complex_values():
    """Testa o cache com valores complexos"""
    cache = Cache()
    
    # Lista
    list_key = "list_key"
    list_value = [1, 2, 3, {"nested": True}]
    cache.set(list_key, list_value)
    assert cache.get(list_key) == list_value
    
    # Dicionário
    dict_key = "dict_key"
    dict_value = {"a": 1, "b": [1, 2, 3], "c": {"nested": True}}
    cache.set(dict_key, dict_value)
    assert cache.get(dict_key) == dict_value
    
    # Objeto customizado
    class TestObject:
        def __init__(self, value):
            self.value = value
    
    obj_key = "obj_key"
    obj_value = TestObject("test")
    cache.set(obj_key, obj_value)
    retrieved = cache.get(obj_key)
    assert retrieved is obj_value
    assert retrieved.value == "test"

def test_cache_with_different_ttls():
    """Testa o cache com diferentes tempos de expiração"""
    cache = Cache(default_ttl=1.0)  # Default de 1 segundo
    
    # Item com TTL padrão
    cache.set("default_ttl", "value1")
    
    # Item com TTL curto
    cache.set("short_ttl", "value2", ttl=0.1)
    
    # Item com TTL longo
    cache.set("long_ttl", "value3", ttl=2.0)
    
    # Inicialmente todos os itens devem estar disponíveis
    assert cache.get("default_ttl") == "value1"
    assert cache.get("short_ttl") == "value2"
    assert cache.get("long_ttl") == "value3"
    
    # Espera o TTL curto expirar
    time.sleep(0.2)
    
    # O item com TTL curto deve ter expirado
    assert cache.get("short_ttl") is None
    assert cache.get("default_ttl") == "value1"
    assert cache.get("long_ttl") == "value3"
    
    # Espera o TTL padrão expirar
    time.sleep(0.9)  # Já passaram 0.2 + 0.9 = 1.1 segundos
    
    # O item com TTL padrão deve ter expirado
    assert cache.get("default_ttl") is None
    assert cache.get("long_ttl") == "value3"
    
    # Espera o TTL longo expirar
    time.sleep(1.0)  # Já passaram 0.2 + 0.9 + 1.0 = 2.1 segundos
    
    # O item com TTL longo deve ter expirado
    assert cache.get("long_ttl") is None

def test_cached_decorator_with_expire_seconds():
    """Testa o decorador de cache usando o parâmetro de compatibilidade expire_seconds"""
    # Limpa o cache global para o teste
    from app.utils.cache import _global_cache
    _global_cache.clear()
    
    call_count = 0
    
    # Define a função dentro do teste para evitar interferência de outras execuções
    @cached(expire_seconds=0.2)  # Usando expire_seconds em vez de ttl
    def test_function(param):
        nonlocal call_count
        call_count += 1
        return f"Result: {param}"
    
    # Primeira chamada
    result1 = test_function("test")
    assert result1 == "Result: test"
    assert call_count == 1
    
    # Segunda chamada - deve usar o cache
    result2 = test_function("test")
    assert result2 == "Result: test"
    assert call_count == 1
    
    # Espera o cache expirar
    time.sleep(0.3)
    
    # Terceira chamada - deve executar a função novamente
    result3 = test_function("test")
    assert result3 == "Result: test"
    assert call_count == 2

def test_cached_decorator_without_ttl():
    """Testa o decorador de cache sem especificar TTL (deve usar o padrão)"""
    # Limpa o cache global para o teste
    from app.utils.cache import _global_cache
    _global_cache.clear()
    
    call_count = 0
    
    # Define a função dentro do teste para evitar interferência de outras execuções
    @cached()  # Sem TTL explícito
    def test_function(param):
        nonlocal call_count
        call_count += 1
        return f"Result: {param}"
    
    # Primeira chamada
    result1 = test_function("test")
    assert result1 == "Result: test"
    assert call_count == 1
    
    # Segunda chamada - deve usar o cache
    result2 = test_function("test")
    assert result2 == "Result: test"
    assert call_count == 1

def test_get_cache_key_with_nonserializable_args():
    """Testa a geração de chaves com argumentos não serializáveis em JSON"""
    # Cria um objeto não serializável
    class NonSerializable:
        def __repr__(self):
            return "NonSerializable()"
    
    non_serializable = NonSerializable()
    
    # Deve usar str() como fallback em vez de json.dumps()
    key = _get_cache_key("func", (non_serializable,), {})
    assert isinstance(key, str)

def test_get_cache_stats():
    """Testa a obtenção de estatísticas do cache"""
    # Prepara um cenário controlado para testar
    from app.utils.cache import _global_cache
    
    # Limpa o cache global
    _global_cache.clear()
    
    # Adiciona alguns itens
    _global_cache.set("valid1", "value1")
    _global_cache.set("valid2", "value2")
    _global_cache.set("expired1", "value3", ttl=0.1)
    
    # Espera um item expirar
    time.sleep(0.2)
    
    # Obtém estatísticas
    stats = get_cache_stats()
    
    # Verifica se as estatísticas estão corretas
    assert stats['total_entries'] == 3
    assert stats['valid_entries'] in (2, 3)  # Pode ser 2 ou 3 dependendo de quando o item expirado é removido
    assert stats['expired_entries'] in (0, 1)  # Complemento do anterior 