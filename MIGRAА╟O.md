## AVISO: DOCUMENTO OBSOLETO

> **Este arquivo foi substituído pelo [DESENVOLVIMENTO_POR_ETAPAS.md](DESENVOLVIMENTO_POR_ETAPAS.md)**  
> **Por favor, utilize o novo documento para acompanhar o progresso atual do projeto.**

---

# Plano de Migração do Projeto TechCare

## Introdução

Este documento apresenta o plano de migração do projeto TechCare/TechZe de uma base de código HTML/CSS/JavaScript para uma aplicação Python moderna usando Flask como framework web. O objetivo é criar uma solução mais robusta, escalável e com diagnósticos reais de sistema em vez de simulações.

## O Que Foi Feito

### 1. Arquitetura e Estrutura do Projeto

- **Estrutura de Diretórios**: Implementação de uma estrutura organizada e modular seguindo boas práticas:
  - `app/`: Pacote principal da aplicação
    - `routes/`: Controladores e rotas da aplicação
    - `services/`: Serviços de negócios (diagnóstico, etc.)
    - `models/`: Modelos de dados e esquemas
    - `templates/`: Templates HTML para renderização
    - `static/`: Arquivos estáticos (CSS, JavaScript, imagens)
  - `config.py`: Configurações da aplicação para diferentes ambientes
  - `run.py`: Ponto de entrada da aplicação

- **Configuração de Ambientes**: Suporte para diferentes ambientes (desenvolvimento, teste, produção) com configurações específicas para cada um.

### 2. Implementação de Diagnóstico Real

- **Serviço de Diagnóstico**: Implementação de um serviço abrangente que realiza verificações reais do sistema:
  - Análise de CPU (uso, núcleos, frequência)
  - Análise de Memória RAM (total, disponível, processos com alto consumo)
  - Análise de Disco (espaço, tipo SSD/HDD, fragmentação)
  - Análise de Programas de Inicialização (Windows)
  - Análise de Drivers (Windows)
  - Análise de Segurança (Windows Defender, Firewall, atualizações)
  - Análise de Rede (interfaces, conectividade)
  - Análise de Temperatura (CPU e componentes)

- **Geração de Relatórios**: Sistema para salvar e recuperar resultados de diagnósticos com histórico.

### 3. Interface e Experiência do Usuário

- **Templates Bootstrap**: Implementação de interface moderna e responsiva usando Bootstrap 5.
- **Interfaces Interativas**: Páginas para diagnóstico, histórico e visualização de resultados.
- **Tema Escuro/Claro**: Sistema de alteração de tema com persistência das preferências do usuário.
- **Visualizações Gráficas**: Implementação de medidores (gauges) e gráficos para visualização de estatísticas.
- **Melhorias de UX**: Animações suaves, transições e feedback visual para interações.

### 4. Backend e Processamento

- **Dependências Python**: Instalação e configuração das bibliotecas necessárias:
  - Flask: Framework web
  - psutil: Monitoramento de recursos do sistema
  - py-cpuinfo: Informações detalhadas da CPU
  - wmi e pywin32: Interação com o Windows Management Instrumentation
  - SQLAlchemy: ORM para banco de dados
  - sensors-core: Monitoramento de temperatura (Linux)

### 5. Autenticação e Autorização

- **Sistema de Login e Registro**: Implementação completa de autenticação de usuários:
  - Páginas de login e registro
  - Gerenciamento de perfil de usuário
  - Proteção de rotas com login_required
  - Diferentes níveis de acesso (admin, técnico, usuário comum)

- **Banco de Dados**: Transição para armazenamento em banco de dados:
  - Modelo de usuário com gerenciamento de senhas seguro
  - Modelo de diagnóstico associado a usuários
  - Persistência de resultados em formato JSON

- **Administração de Usuários**: Interface para administradores gerenciarem usuários:
  - Listagem de todos os usuários
  - Edição de perfis (nome, email, função, status)
  - Redefinição de senhas

### 6. Scripts e Configuração

- **Script de Inicialização**: Implementação de script para inicializar o banco de dados:
  - Criação de usuários padrão (admin, técnico, usuário)
  - Estruturação inicial do banco de dados

- **Script de Configuração**: Implementação de script para configurar o ambiente:
  - Criação de diretórios necessários
  - Configuração do ambiente virtual
  - Instalação de dependências
  - Inicialização do banco de dados

### 7. Sistema de Reparo Guiado

- **Serviço de Reparo**: Implementação de um serviço que fornece guias de reparo passo a passo para problemas detectados:
  - Organização de guias por categoria (CPU, memória, disco, etc.)
  - Instruções detalhadas para resolução de problemas
  - Estrutura para automação futura de alguns reparos

- **Interface de Reparo**: Desenvolvimento de páginas para o fluxo de reparo:
  - Exibição do plano de reparo baseado nos problemas detectados
  - Visualização de passos individuais com instruções detalhadas
  - Sistema de progresso e marcação de conclusão de tarefas
  - Relatório final após a conclusão dos reparos

### 8. Sistema de Atualização de Drivers

- **Serviço de Atualização de Drivers**: Desenvolvimento de serviço para:
  - Detecção de dispositivos e drivers instalados
  - Verificação de versões mais recentes
  - Download e instalação automática de drivers atualizados
  - Backup de drivers antigos antes da atualização

- **Interface de Drivers**: Implementação de páginas para:
  - Visualização de dispositivos e status dos drivers
  - Opções para atualização individual ou em massa
  - Histórico de atualizações e restauração de drivers

### 9. Sistema de Limpeza e Otimização

- **Serviço de Limpeza (CleanerService)**: Implementação completa de funcionalidades similares ao CCleaner Pro:
  - Análise e limpeza de arquivos temporários do sistema
  - Limpeza de cache, cookies e histórico de navegadores
  - Otimização e reparo do registro do Windows
  - Gerenciamento de programas de inicialização do sistema
  - Reparo de arquivos corrompidos do sistema
  - Análise de espaço em disco e identificação de arquivos grandes
  - Verificação e reparo de problemas no disco

- **Interface de Limpeza**: Desenvolvimento de um dashboard completo:
  - Visualização de análise do sistema com métricas de espaço a ser liberado
  - Cartões para diferentes funcionalidades (limpeza, registro, inicialização, reparo)
  - Opções para limpeza individual ou completa do sistema
  - Resultados detalhados das análises realizadas

### 10. Sistema de Testes Automatizados

- **Estrutura de Testes**: Configuração de uma estrutura completa para testes automatizados:
  - Configuração do pytest como framework principal de testes
  - Implementação de fixtures para configurar ambientes de teste
  - Organização de testes por categoria (modelos, serviços, rotas)
  - Configuração de relatórios de cobertura de código

- **Testes de Serviços**: Implementação de testes unitários para os principais serviços:
  - Testes do serviço de diagnóstico com mocks para simulação de recursos do sistema
  - Testes do serviço de limpeza com simulação de arquivos e registros
  - Testes do serviço de reparo com simulação de problemas e planos
  - Testes do serviço de drivers com mocks para WMI e APIs
  - Testes isolados que não dependem de recursos reais do sistema

- **Testes de Modelos**: Implementação de testes para modelos de dados:
  - Verificação de funções de hashing de senha e autenticação
  - Validação de papéis e permissões de usuário
  - Testes de representação e serialização de objetos
  - Verificação do comportamento de alteração de senha e status de usuário

- **Testes de Rotas**: Implementação de testes para as principais rotas da aplicação:
  - Rotas de autenticação (login, logout, registro)
  - Rotas de diagnóstico (execução, histórico, detalhes)
  - Testes de acesso a rotas protegidas

### 11. Limpeza de Código

- [x] Remover arquivos legados da versão em JavaScript
- [x] Consolidar arquivos CSS duplicados
- [x] Migrar scripts JavaScript restantes para a estrutura Flask
- [x] Configurar estrutura de testes automatizados
- [ ] Documentar funções e classes com docstrings consistentes

Um script de limpeza foi implementado (`scripts/cleanup_legacy_files.py`) para remover arquivos da versão JavaScript que não são mais necessários. Este script:

1. Identifica todos os arquivos JS, HTML e CSS da versão antiga
2. Faz backup dos arquivos antes de removê-los
3. Remove os arquivos de forma segura após confirmação do usuário

Isso ajuda a manter o projeto organizado e reduzir confusão entre a versão antiga e a nova implementação Python.

## Próximos Passos

### 1. Funcionalidades Adicionais

- [x] Sistema de reparo guiado passo a passo
- [x] Sistema de atualização de drivers (similar ao site de referência)
- [x] Sistema de limpeza e otimização (similar ao CCleaner Pro)
- [ ] Módulo de backup e restauração de arquivos importantes
- [ ] Sistema de notificações para problemas críticos

### 2. Melhorias de Diagnóstico

- [x] Adicionar análise de temperatura de componentes
- [x] Implementar detecção e atualização de drivers desatualizados
- [ ] Implementar diagnóstico de hardware mais detalhado (GPU, periféricos)
- [ ] Adicionar benchmarks para comparação de desempenho
- [ ] Implementar verificação de malware e vírus

### 3. Interface e UX

- [x] Melhorar visualização de resultados com gráficos e indicadores
- [x] Adicionar tema escuro
- [x] Implementar recursos de acessibilidade e responsividade
- [ ] Implementar dashboard para técnicos com visão geral dos sistemas
- [ ] Desenvolver versão PWA completa para uso offline

### 4. Segurança e Robustez

- [x] Configurar estrutura básica de testes automatizados
- [x] Implementar testes unitários para serviços principais
- [x] Implementar testes para modelos de dados
- [x] Implementar testes para rotas de autenticação
- [x] Implementar testes para rotas de diagnóstico
- [ ] Implementar testes de integração para fluxos completos
- [ ] Adicionar autenticação via tokens (JWT)
- [ ] Implementar verificações de segurança e sanitização de entradas
- [ ] Adicionar logs detalhados e sistema de monitoramento

### 5. Implantação

- [ ] Criar script de instalação para diferentes sistemas
- [ ] Configurar CI/CD para implantação contínua
- [ ] Preparar pacote de distribuição para Windows
- [ ] Documentação detalhada para usuários finais

### 6. Limpeza de Código

- [x] Remover arquivos legados da versão em JavaScript
- [x] Consolidar arquivos CSS duplicados
- [x] Migrar scripts JavaScript restantes para a estrutura Flask
- [ ] Aumentar cobertura de testes (meta: 80% do código)
- [ ] Documentar funções e classes com docstrings consistentes

## Cronograma Sugerido

1. **Fase 1 (CONCLUÍDA)**: Base da aplicação e diagnóstico inicial
2. **Fase 2 (CONCLUÍDA)**: Funcionalidades de autenticação e banco de dados
3. **Fase 3 (CONCLUÍDA)**: Melhorias no diagnóstico e sistema de reparo guiado
4. **Fase 4 (CONCLUÍDA)**: Sistema de atualização de drivers e limpeza do sistema
5. **Fase 5 (CONCLUÍDA)**: Limpeza de código e remoção de arquivos legados
6. **Fase 6 (CONCLUÍDA)**: Aprimoramentos de interface e experiência do usuário
7. **Fase 7 (EM ANDAMENTO)**: Testes, segurança e preparação para implantação
   - [x] Configuração da estrutura de testes
   - [x] Implementação de testes unitários básicos
   - [x] Ampliação da cobertura de testes para serviços principais
   - [x] Implementação de testes para modelos de dados
   - [x] Implementação de testes para rotas de autenticação
   - [x] Implementação de testes para rotas de diagnóstico
   - [ ] Implementação de testes de integração
   - [ ] Melhorias de segurança
   - [ ] Configuração de CI/CD para verificação automática de testes

## Conclusão

O projeto TechCare evoluiu significativamente da versão original, sendo agora uma aplicação Python moderna com diagnósticos reais de sistema, autenticação de usuários e armazenamento em banco de dados. A arquitetura modular e as boas práticas implementadas permitem uma fácil expansão das funcionalidades e manutenção a longo prazo.

Com a conclusão da Fase 6, temos um sistema completo com diagnósticos avançados, sistema de reparo guiado, atualização de drivers e limpeza/otimização do sistema, além de uma interface de usuário moderna com tema escuro/claro e visualizações interativas de dados.

Na Fase 7, estamos avançando na implementação de testes automatizados para garantir a robustez do sistema. Já configuramos a estrutura básica de testes com pytest e implementamos testes unitários para os principais componentes:

1. Testes para o serviço de diagnóstico que verificam a inicialização correta e a detecção de problemas de CPU, memória e disco
2. Testes para o serviço de limpeza que verificam a análise de arquivos temporários, cache de navegadores e registro do Windows
3. Testes para o serviço de reparo que verificam a geração de planos e acompanhamento de progresso
4. Testes para o serviço de drivers que verificam a detecção, verificação de atualizações e download
5. Testes para o modelo de usuário que verificam funções de autenticação, validação de papéis e gerenciamento de senhas
6. Testes para rotas de autenticação e diagnóstico que verificam o funcionamento das principais interfaces da aplicação

A implementação de testes automatizados está bem avançada, com boa cobertura dos componentes principais. No entanto, ainda precisamos implementar testes de integração para verificar o funcionamento em conjunto dos diferentes componentes e melhorar ainda mais a cobertura de código.

O TechCare agora se posiciona como uma solução completa e moderna para diagnóstico, reparo, atualização de drivers e otimização de sistemas, com uma interface intuitiva e agradável, tornando-se uma ferramenta valiosa tanto para técnicos quanto para usuários finais.

# Exemplo de implementação para tests/test_services/test_diagnostic_service.py
import pytest
from unittest.mock import patch, MagicMock
from app.services.diagnostic_service import DiagnosticService

def test_diagnostic_service_initialization():
    """Testa a inicialização do serviço de diagnóstico."""
    service = DiagnosticService()
    assert service.results is not None
    assert service.problems == []
    assert service.score == 100

@patch('psutil.cpu_percent')
def test_analyze_cpu(mock_cpu_percent):
    """Testa a análise de CPU simulando um uso alto."""
    mock_cpu_percent.return_value = 90
    
    service = DiagnosticService()
    service.analyze_cpu()
    
    # Verifica se detectou problema de CPU alta
    assert len(service.problems) > 0
    cpu_problem = next((p for p in service.problems if p['category'] == 'cpu'), None)
    assert cpu_problem is not None
    assert 'Alto uso de CPU' in cpu_problem['title']
    assert service.score < 100

# Exemplo para tests/test_services/test_cleaner_service.py
import pytest
from unittest.mock import patch, MagicMock
import os
from app.services.cleaner_service import CleanerService

@patch('os.path.exists')
@patch('os.path.getsize')
def test_analyze_temp_files(mock_getsize, mock_exists):
    """Testa a análise de arquivos temporários."""
    mock_exists.return_value = True
    mock_getsize.return_value = 1024 * 1024 * 100  # 100 MB
    
    service = CleanerService()
    result = service.analyze_temp_files()
    
    assert result['size_bytes'] > 0
    assert 'temp_files' in result
    assert len(result['temp_files']) > 0 