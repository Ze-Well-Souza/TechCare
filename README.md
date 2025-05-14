<<<<<<< HEAD
# TechCare
O TechCare é um sistema híbrido de manutenção de computadores que oferece diagnóstico automatizado, serviços de otimização e suporte técnico remoto/presencial. O site foi desenvolvido com tecnologias modernas e está pronto para uso imediato.
=======
# TechCare - Sistema de Manutenção e Diagnóstico de Computadores

## 📋 Descrição
TechCare é uma aplicação web desenvolvida em Python Flask para diagnóstico e manutenção de computadores Windows. O sistema realiza análise de diversos componentes do sistema, incluindo CPU, memória, disco, rede e registro, oferecendo recomendações e ferramentas de correção.

## ✨ Funcionalidades

### 🔍 Diagnóstico de Sistema
- Análise de CPU e desempenho
- Análise de memória RAM
- Análise de disco e armazenamento
- Análise de rede
- Diagnóstico de inicialização

### 🧹 Sistema de Limpeza
- Limpeza de arquivos temporários
- Remoção de cache de navegadores
- Limpeza de logs e arquivos desnecessários
- Agendamento de limpezas periódicas

### 🔧 Sistema de Reparo
- Correção de problemas no registro do Windows
- Otimização de inicialização
- Log detalhado de ações e reparos

### 🔄 Atualização de Drivers
- Detecção de drivers instalados
- Verificação de drivers desatualizados
- Backup e restauração de drivers

### 📊 Visualização e Relatórios
- Gráficos de desempenho do sistema
- Histórico de diagnósticos
- Comparação de resultados antes e depois
- Exportação de relatórios

## 🛠️ Tecnologias Utilizadas
- **Flask**: Framework web
- **SQLAlchemy**: ORM para banco de dados
- **Pandas e Plotly**: Análise de dados e visualizações
- **WMI e PyWin32**: Interação com sistema Windows
- **Pytest**: Framework de testes

## 📦 Instalação e Execução

### Requisitos
- Python 3.8 ou superior
- Windows 10/11 (algumas funcionalidades são específicas para Windows)

### Instalação
1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/techcare.git
cd techcare
```

2. Crie e ative um ambiente virtual
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Instale as dependências
```bash
pip install -r requirements.txt
```

4. Execute a aplicação
```bash
python run_local.py
```

5. Acesse a aplicação em `http://localhost:5000`

## 🚀 Deploy no PythonAnywhere
O TechCare pode ser hospedado no PythonAnywhere. Consulte o arquivo `DEPLOY_PYTHONANYWHERE.md` para instruções detalhadas.

## 📝 Licença
Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

## 👥 Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e enviar pull requests.

## 🔄 Status do Projeto
O projeto está em fase avançada de desenvolvimento com todos os módulos principais implementados e testados.

## 🧪 Testes
Para executar os testes:
```bash
python -m pytest tests/
```

Para verificar a cobertura de código:
```bash
python -m pytest --cov=app tests/
```

## 📞 Contato
Para mais informações, entre em contato através do GitHub ou email.

---
Última atualização: 14/05/2025
>>>>>>> 75bb5cb (Commit inicial do projeto TechCare)
