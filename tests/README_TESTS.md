# Documentação de Testes - TechCare

Este documento descreve a estrutura de testes automatizados do projeto TechCare, incluindo orientações de como executar os testes e contribuir com novos testes.

## Estrutura de Testes

Os testes estão organizados seguindo a estrutura do projeto:

```
tests/
├── conftest.py              # Configurações e fixtures compartilhadas
├── test_models/             # Testes para modelos de dados
│   ├── test_user.py
│   └── ...
├── test_services/           # Testes para serviços de negócios
│   ├── test_diagnostic_service.py
│   ├── test_cleaner_service.py
│   ├── test_repair_service.py
│   ├── test_driver_service.py
│   └── ...
├── test_routes/             # Testes para rotas e endpoints
│   ├── test_auth_routes.py
│   ├── test_diagnostic_routes.py
│   └── ...
└── coverage_html/           # Relatórios de cobertura de testes (gerados)
```

## Tecnologias Utilizadas

- **pytest**: Framework principal de testes
- **pytest-cov**: Plugin para geração de relatórios de cobertura
- **unittest.mock**: Biblioteca para criação de mocks e simulações

## Como Executar os Testes

### Executar Todos os Testes

```bash
python -m pytest
```

### Executar com Relatório de Cobertura

```bash
python -m pytest --cov=app
```

### Executar Testes Específicos

```bash
# Executar testes de um módulo específico
python -m pytest tests/test_services/test_diagnostic_service.py

# Executar um teste específico
python -m pytest tests/test_services/test_diagnostic_service.py::test_analyze_cpu

# Executar testes com palavras-chave específicas no nome
python -m pytest -k "cpu"
```

## Fixtures Disponíveis

O arquivo `conftest.py` define fixtures reutilizáveis para os testes:

- **app**: Instância do aplicativo Flask configurada para testes
- **client**: Cliente HTTP para testar requisições
- **runner**: Runner para comandos CLI
- **test_user**: Usuário comum para testes
- **test_admin**: Usuário administrador para testes
- **test_technician**: Usuário técnico para testes
- **auth_client**: Cliente HTTP com login já realizado como usuário comum
- **admin_client**: Cliente HTTP com login já realizado como administrador

## Estratégias de Mock

Para testes que dependem de recursos do sistema ou APIs externas, utilizamos mocks para simular essas dependências:

### Exemplo para psutil

```python
@patch('psutil.cpu_percent')
def test_analyze_cpu(mock_cpu_percent):
    mock_cpu_percent.return_value = 90  # Simula 90% de uso da CPU
    
    service = DiagnosticService()
    service.analyze_cpu()
    
    # Verifica se o problema foi detectado corretamente
    assert len(service.problems) > 0
```

### Exemplo para WMI (Windows Management Instrumentation)

```python
@patch('wmi.WMI')
def test_scan_drivers(mock_wmi):
    # Configura os mocks para dispositivos
    mock_device = MagicMock()
    mock_device.Caption = "Dispositivo de Teste"
    mock_device.DriverVersion = "1.0.0"
    
    mock_wmi_instance = MagicMock()
    mock_wmi_instance.Win32_PnPSignedDriver.return_value = [mock_device]
    mock_wmi.return_value = mock_wmi_instance
    
    service = DriverService()
    drivers = service.scan_drivers()
    
    assert len(drivers) == 1
    assert drivers[0]['name'] == "Dispositivo de Teste"
```

## Cobertura de Testes Atual

A cobertura de testes atual abrange:

- **Modelos**: Testes para o modelo de usuário, incluindo autenticação e gerenciamento de funções
- **Serviços**:
  - Serviço de diagnóstico: CPU, memória, disco
  - Serviço de limpeza: Arquivos temporários, cache de navegadores, registro do Windows
  - Serviço de drivers: Detecção, verificação de atualizações, download
  - Serviço de reparo: Geração de planos, passos, acompanhamento
- **Rotas**:
  - Autenticação: Login, logout, registro
  - Diagnóstico: Execução, histórico, detalhes

## Áreas para Expansão de Testes

As seguintes áreas ainda precisam de mais testes:

1. **Testes de integração** entre componentes
2. **Testes de serviços** para funcionalidades avançadas:
   - Temperatura do sistema
   - Análise de rede
   - Inicialização do sistema
3. **Testes para as rotas**:
   - Rotas de limpeza
   - Rotas de atualização de drivers
   - Rotas de reparo
4. **Testes de interface de usuário** e JavaScript:
   - Funcionamento de gráficos e visualizações
   - Tema escuro/claro
   - Interatividade

## Como Adicionar Novos Testes

1. Identifique o diretório apropriado com base no tipo de componente a ser testado
2. Crie um novo arquivo de teste seguindo a convenção `test_*.py`
3. Implemente os testes usando as ferramentas e fixtures disponíveis
4. Execute os testes para verificar se estão funcionando corretamente
5. Verifique a cobertura para garantir que os principais caminhos de código são testados

### Exemplo Básico

```python
import pytest
from app.services.example_service import ExampleService

def test_example_functionality():
    service = ExampleService()
    result = service.do_something()
    assert result == expected_value
```

## Boas Práticas

1. **Isole os testes**: Cada teste deve ser independente e não depender de outros testes
2. **Use mocks apropriadamente**: Não teste dependências externas, apenas o código da aplicação
3. **Nomeie os testes claramente**: O nome deve indicar o que está sendo testado
4. **Documente os testes**: Adicione docstrings para explicar o propósito do teste
5. **Mantenha testes simples**: Um teste deve testar uma única funcionalidade ou comportamento
6. **Verifique casos de borda**: Teste limites e casos excepcionais, não apenas o caminho feliz 