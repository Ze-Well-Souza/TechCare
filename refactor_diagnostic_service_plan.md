# Plano de Refatoração do DiagnosticService

## Análise do Problema

O arquivo `diagnostic_service.py` atual tem mais de 3000 linhas, o que dificulta a manutenção e pode causar problemas de desempenho e consumo de memória. Quando arquivos ficam muito grandes, tendem a:

1. Carregar muitas dependências desnecessárias em cada execução
2. Dificultar o teste unitário
3. Aumentar o consumo de memória por manter muitos recursos carregados
4. Impedir a aplicação do princípio de responsabilidade única

## Objetivos da Refatoração

- Reduzir o consumo de memória do módulo de diagnóstico
- Melhorar a manutenibilidade do código
- Facilitar os testes unitários
- Separar funcionalidades por responsabilidade
- Melhorar o desempenho do diagnóstico

## Estrutura Proposta

Dividir o `DiagnosticService` em módulos menores com responsabilidades específicas:

```
app/services/diagnostic/
├── __init__.py              # Expõe a API principal
├── diagnostic_service.py    # Classe principal (simplificada, apenas orquestra)
├── analyzers/               # Módulos específicos para cada tipo de análise
│   ├── __init__.py
│   ├── cpu_analyzer.py      # Análise de CPU
│   ├── memory_analyzer.py   # Análise de memória
│   ├── disk_analyzer.py     # Análise de disco
│   ├── network_analyzer.py  # Análise de rede
│   ├── startup_analyzer.py  # Análise de inicialização
│   ├── driver_analyzer.py   # Análise de drivers
│   ├── security_analyzer.py # Análise de segurança
│   └── temp_analyzer.py     # Análise de temperatura
├── reporters/               # Formatação e geração de relatórios
│   ├── __init__.py
│   ├── report_generator.py  # Geração de relatórios
│   └── recommendations.py   # Geração de recomendações
├── utils/                   # Utilitários compartilhados
│   ├── __init__.py
│   ├── platform_utils.py    # Utilitários específicos de plataforma
│   ├── wmi_utils.py         # Utilitários para WMI (Windows)
│   └── linux_utils.py       # Utilitários para Linux
└── repositories/            # Acesso aos dados
    ├── __init__.py
    └── diagnostic_repository.py  # Repositório refatorado
```

## Plano de Implementação

### Fase 1: Preparar a Nova Estrutura

1. Criar a nova estrutura de diretórios
2. Criar arquivos `__init__.py` vazios para cada pacote
3. Desenvolver uma versão básica da nova classe `DiagnosticService` que orquestrará os módulos

### Fase 2: Implementar os Analisadores Específicos

Para cada analisador:

1. Extrair o código relacionado a cada análise do arquivo original
2. Criar uma classe específica (ex.: `CPUAnalyzer`, `MemoryAnalyzer`, etc.)
3. Implementar interface consistente com métodos como `analyze()` e `get_issues()`
4. Garantir que cada classe carregue apenas as dependências necessárias
5. Adicionar lazy loading (importações apenas quando necessário)

### Fase 3: Implementar Camada de Relatórios

1. Extrair o código de geração de relatório para `report_generator.py`
2. Implementar classes específicas para formatação de diferentes tipos de saídas
3. Separar a lógica de recomendações em uma classe dedicada

### Fase 4: Implementar Utilitários Compartilhados

1. Identificar funções de utilidade usadas em múltiplos analisadores
2. Extrair para módulos de utilitários apropriados
3. Implementar inicialização lazy dos recursos (ex.: conexões WMI)

### Fase 5: Migrar Repositório de Dados

1. Refatorar `DiagnosticRepository` para nova estrutura
2. Garantir compatibilidade com métodos existentes

### Fase 6: Implementação do Novo DiagnosticService

1. Implementar a classe principal que orquestrará todos os componentes
2. Garantir compatibilidade com a API anterior
3. Implementar lazy loading dos analisadores

### Fase 7: Testes e Validação

1. Escrever testes para cada componente individualmente
2. Escrever testes de integração entre componentes
3. Validar que não há regressões na funcionalidade
4. Medir o consumo de memória antes e depois

## Otimizações de Memória Específicas

1. **Lazy Loading de Módulos**:
   ```python
   def analyze_cpu(self):
       from app.services.diagnostic.analyzers.cpu_analyzer import CPUAnalyzer
       analyzer = CPUAnalyzer()
       return analyzer.analyze()
   ```

2. **Liberação Explícita de Recursos**:
   ```python
   def analyze_wmi_data(self):
       import gc
       try:
           # Código de análise...
           return result
       finally:
           # Liberar recursos explicitamente
           gc.collect()
   ```

3. **Minimizar Variáveis Globais**:
   - Converter variáveis globais em parâmetros de função
   - Utilizar configuração central injetada nos componentes

4. **Usar Geradores em vez de Listas**:
   ```python
   # Antes
   def get_all_processes():
       return [p for p in psutil.process_iter()]
   
   # Depois
   def get_all_processes():
       for p in psutil.process_iter():
           yield p
   ```

5. **Evitar Carga Desnecessária de Dados**:
   - Implementar paginação em consultas de histórico
   - Filtrar dados no banco em vez de na memória

## Métricas e Validação

1. **Métricas Antes da Refatoração**:
   - Tamanho do arquivo (linhas de código)
   - Consumo de memória durante execução
   - Tempo de execução de diagnóstico completo
   - Tempo de importação do módulo

2. **Métricas Após a Refatoração**:
   - Mesmas métricas para comparação
   - Tamanho de cada novo módulo
   - Consumo de memória por módulo

## Cronograma Estimado

- **Fase 1**: 1 dia
- **Fase 2**: 3-4 dias (0.5 dia por analisador)
- **Fase 3**: 1 dia
- **Fase 4**: 1 dia
- **Fase 5**: 0.5 dia
- **Fase 6**: 1 dia
- **Fase 7**: 2 dias

**Total**: 9-10 dias de trabalho

## Riscos e Mitigações

1. **Risco**: Regressões em funcionalidade
   **Mitigação**: Testes abrangentes e execução em paralelo com versão antiga

2. **Risco**: Dificuldade em manter compatibilidade com API atual
   **Mitigação**: Implementar camada de compatibilidade no módulo principal

3. **Risco**: Dependências circulares entre novos módulos
   **Mitigação**: Arquitetura clara e revisões de código durante refatoração

4. **Risco**: Perda de desempenho devido à fragmentação excessiva
   **Mitigação**: Medir desempenho continuamente e ajustar conforme necessário 