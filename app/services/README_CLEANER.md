# Serviço de Limpeza e Otimização do TechCare

Este documento descreve o funcionamento do serviço de limpeza e otimização (CleanerService) do TechCare, uma implementação similar ao CCleaner Pro.

## Visão Geral

O CleanerService oferece funcionalidades completas para limpeza, otimização e reparo do sistema, permitindo aos usuários:

- Analisar e limpar arquivos temporários do sistema
- Limpar cache, cookies e histórico de navegadores
- Otimizar e reparar o registro do Windows
- Gerenciar programas de inicialização do sistema
- Reparar arquivos corrompidos do sistema
- Analisar espaço em disco e identificar arquivos grandes
- Verificar e reparar problemas no disco

## Implementação

### Estrutura de Arquivos

- `app/services/cleaner_service.py` - Implementação do serviço de limpeza
- `app/routes/cleaner.py` - Rotas de API e páginas para o serviço de limpeza
- `app/templates/cleaner/dashboard.html` - Interface principal do serviço
- `app/templates/cleaner/analysis_results.html` - Visualização detalhada dos resultados da análise

### Classes e Métodos Principais

O serviço utiliza a classe `CleanerService` com os seguintes métodos principais:

#### Análise do Sistema

- `analyze_system()` - Realiza análise completa do sistema
- `_analyze_temp_files()` - Analisa arquivos temporários
- `_analyze_browser_data()` - Analisa dados de navegadores
- `_analyze_startup_items()` - Analisa itens de inicialização
- `_analyze_registry()` - Analisa problemas no registro do Windows
- `_analyze_disk_space()` - Analisa espaço em disco disponível
- `_find_large_files()` - Encontra arquivos grandes no sistema
- `_check_corrupted_files()` - Verifica arquivos corrompidos do sistema

#### Ações de Limpeza

- `clean_temp_files()` - Limpa arquivos temporários do sistema
- `clean_browser_cache(browsers)` - Limpa cache de navegadores específicos
- `repair_system_files()` - Repara arquivos do sistema via SFC e DISM
- `clean_registry()` - Limpa e repara o registro do Windows
- `optimize_startup(items_to_disable)` - Otimiza inicialização do sistema
- `verify_disk()` - Verifica e repara problemas no disco

## API REST

As seguintes rotas estão disponíveis para interação com o serviço de limpeza:

- `GET /cleaner/dashboard` - Exibe o dashboard principal com análise do sistema
- `GET /cleaner/analyze` - Analisa o sistema e retorna resultados (HTML ou JSON)
- `POST /cleaner/clean-temp` - Limpa arquivos temporários
- `POST /cleaner/clean-browser` - Limpa cache de navegadores
- `POST /cleaner/clean-registry` - Limpa e repara o registro
- `POST /cleaner/optimize-startup` - Otimiza itens de inicialização
- `POST /cleaner/repair-system` - Repara arquivos do sistema
- `POST /cleaner/verify-disk` - Verifica e repara problemas no disco

## Configuração e Dependências

O serviço requer as seguintes dependências:

- psutil: Informações sobre o sistema e processos
- winreg: Acesso ao registro do Windows
- shutil, os, subprocess: Manipulação de arquivos e execução de comandos

## Segurança e Permissões

⚠️ **IMPORTANTE**: Para funções como limpeza de registro e reparo de sistema, o TechCare deve ser executado com privilégios administrativos no Windows.

## Comportamento em Diferentes Sistemas Operacionais

- No Windows: Todas as funcionalidades estão disponíveis (limpeza de registro, reparo do sistema, etc.)
- Em outros sistemas (Linux/macOS): Funcionalidades específicas do Windows são desativadas automaticamente

## Interface com o Usuário

A interface é projetada para ser intuitiva, com:

- Dashboard visual com métricas de limpeza
- Cartões para diferentes funcionalidades (limpeza, registro, inicialização, reparo)
- Botões para ações individuais ou limpeza completa
- Visualização detalhada dos resultados da análise

## Exemplos de Uso (Código)

### Criação do serviço e análise
```python
from app.services.cleaner_service import CleanerService

# Cria o serviço de limpeza
cleaner = CleanerService()

# Analisa o sistema
results = cleaner.analyze_system()
print(f"Espaço a ser liberado: {results['total_cleanup_formatted']}")
```

### Limpeza de arquivos temporários
```python
# Limpa arquivos temporários
result = cleaner.clean_temp_files()
if result['success']:
    print(f"Liberado: {result['cleaned_size_formatted']}")
```

### Limpeza de navegadores específicos
```python
# Limpa cache do Chrome e Firefox
result = cleaner.clean_browser_cache(['chrome', 'firefox'])
if result['success']:
    print(f"Cache de navegadores limpo: {result['cleaned_size_formatted']}")
``` 