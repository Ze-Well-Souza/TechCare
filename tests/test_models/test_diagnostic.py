import pytest
from app.models.diagnostic import Diagnostic
from datetime import datetime

def test_cpu_results_serialization():
    diag = Diagnostic(name='PC')
    data = {'usage': 80, 'temp': 60}
    diag.set_cpu_results(data)
    assert diag.get_cpu_results() == data

def test_memory_results_serialization():
    diag = Diagnostic(name='PC')
    data = {'total': 8, 'used': 4}
    diag.set_memory_results(data)
    assert diag.get_memory_results() == data

def test_disk_results_serialization():
    diag = Diagnostic(name='PC')
    data = {'C:': {'free': 100}}
    diag.set_disk_results(data)
    assert diag.get_disk_results() == data

def test_startup_results_serialization():
    diag = Diagnostic(name='PC')
    data = {'apps': ['A', 'B']}
    diag.set_startup_results(data)
    assert diag.get_startup_results() == data

def test_driver_results_serialization():
    diag = Diagnostic(name='PC')
    data = {'drivers': ['ok']}
    diag.set_driver_results(data)
    assert diag.get_driver_results() == data

def test_security_results_serialization():
    diag = Diagnostic(name='PC')
    data = {'antivirus': 'ok'}
    diag.set_security_results(data)
    assert diag.get_security_results() == data

def test_network_results_serialization():
    diag = Diagnostic(name='PC')
    data = {'ping': 10}
    diag.set_network_results(data)
    assert diag.get_network_results() == data

def test_timestamp_property():
    diag = Diagnostic(name='PC')
    # O campo timestamp pode ser None se não houver integração com o banco
    # O teste deve aceitar ambos os casos
    ts = diag.timestamp
    assert ts is None or isinstance(ts, datetime)

def test_repr():
    diag = Diagnostic(name='PC')
    r = repr(diag)
    assert 'Diagnostic' in r and 'PC' in r 