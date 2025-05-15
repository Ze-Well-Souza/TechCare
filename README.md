# TechCare - Sistema de Manutenção de Computadores

## Descrição
TechCare é um sistema completo para diagnóstico, manutenção e otimização de computadores. Desenvolvido em Python/Flask, oferece uma interface web intuitiva para realizar diagnósticos de hardware e software, limpar sistemas, atualizar drivers e gerar relatórios detalhados.

## Principais Funcionalidades
- Diagnóstico completo de sistema (CPU, memória, disco, rede)
- Limpeza de arquivos temporários e otimização de disco
- Atualização e reparo de drivers
- Otimização de inicialização
- Reparo de registros do Windows
- Relatórios detalhados com gráficos interativos
- API REST para integrações externas

## Arquitetura
O projeto segue uma arquitetura MVC com:
- **Models**: Representações das entidades do banco de dados
- **Views**: Templates Flask com Jinja2
- **Controllers**: Rotas Flask organizadas por módulo
- **Services**: Lógica de negócio encapsulada em classes de serviço
- **Repositories**: Camada de acesso aos dados

## Tecnologias Utilizadas
- **Backend**: Python 3.12, Flask, SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap, Plotly.js
- **Banco de Dados**: SQLite (desenvolvimento), PostgreSQL (produção)
- **Diagnóstico**: Bibliotecas psutil, wmi, win32com
- **Testes**: Pytest, Coverage

## Status do Projeto
O projeto encontra-se em fase avançada de desenvolvimento, com a maioria das funcionalidades principais implementadas e testadas. Os módulos de diagnóstico, limpeza, reparo e atualização estão operacionais.

### Próximos Passos
- Otimização de memória
- Suporte a múltiplos bancos de dados
- Compatibilidade multi-plataforma (Linux, macOS)
- Análise preditiva com machine learning
- Desenvolvimento de aplicativo móvel

## Documentação
Para informações detalhadas sobre o estado atual do projeto, tarefas concluídas, pendências e planos de desenvolvimento futuros, consulte o arquivo **[TASK_MASTER.md](TASK_MASTER.md)**.

## Requisitos
- Python 3.11+ 
- Windows 10+ (para funcionalidades completas)
- Linux/macOS (suporte parcial, em desenvolvimento)

## Instalação e Execução

### Desenvolvimento Local
```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/techcare.git
cd techcare

# Configurar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
python run_local.py
```

### Testes
```bash
# Executar todos os testes
python run_complete_test_suite.py

# Executar testes específicos
pytest tests/test_diagnostic_service.py
```

## Deploy
Para informações sobre deploy no PythonAnywhere, consulte o arquivo **[DEPLOY_PYTHONANYWHERE.md](DEPLOY_PYTHONANYWHERE.md)**.

## Contribuição
Contribuições são bem-vindas! Por favor, leia o guia de contribuição antes de enviar pull requests.

## Licença
Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para mais detalhes.
