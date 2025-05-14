import os
import shutil
import glob
import sys
import subprocess
import argparse
from pathlib import Path
import datetime

def print_colored(text, color):
    """Imprimir texto colorido no terminal."""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'reset': '\033[0m'
    }
    print(f"{colors.get(color, '')}{text}{colors['reset']}")

def get_confirmation(message, auto_yes=False):
    """Solicitar confirmação do usuário."""
    if auto_yes:
        print(f"{message} (s)")
        return True
    response = input(f"{message} (s/n): ").lower()
    return response.startswith('s')

def clean_pycache():
    """Remover todos os arquivos de cache do Python."""
    print_colored("Limpando caches Python...", "blue")
    
    # Remover __pycache__ e arquivos .pyc
    pycache_dirs = list(Path('.').glob('**/__pycache__'))
    pyc_files = list(Path('.').glob('**/*.pyc'))
    
    count = 0
    for item in pycache_dirs:
        if os.path.exists(item):
            print(f"Removendo {item}")
            shutil.rmtree(item)
            count += 1
    
    for item in pyc_files:
        if os.path.exists(item):
            print(f"Removendo {item}")
            os.remove(item)
            count += 1
    
    print_colored(f"Limpeza concluída. Removidos {count} caches Python.", "green")

def clean_temp_files():
    """Remover arquivos temporários."""
    print_colored("Removendo arquivos temporários...", "blue")
    
    # Padrões de arquivos temporários
    temp_patterns = [
        '**/*.tmp',
        '**/*.bak',
        '**/*.swp',
        '**/.DS_Store',
        '**/Thumbs.db',
        '**/*.log',
        'resultado_testes*.txt'
    ]
    
    count = 0
    for pattern in temp_patterns:
        for file in glob.glob(pattern, recursive=True):
            print(f"Removendo {file}")
            os.remove(file)
            count += 1
    
    print_colored(f"Limpeza concluída. Removidos {count} arquivos temporários.", "green")

def clean_duplicate_docs():
    """Remover documentações duplicadas e mesclar em um único arquivo."""
    print_colored("Organizando documentação...", "blue")
    
    # Lista de arquivos de documentação sobre deploy no PythonAnywhere
    deploy_docs = [
        'DEPLOY_PYTHONANYWHERE.md',
        'README_PYTHONANYWHERE.md',
        'README_DEPLOY_PYTHONANYWHERE.md',
        'README_HOSPEDAGEM_PYTHONANYWHERE.md',
        'GUIA_PYTHONANYWHERE.md',
        'pythonanywhere_deploy_guide.md',
        'steps_to_deploy.md',
        'guia_visual_deploy.md',
        'techcare_pythonanywhere_guide.md',
        'fix_pandas_pythonanywhere.md',
        'static_files_config.md',
        'deploy_zewell10_simplificado.md',
        'setup_virtualenv.md'
    ]
    
    # Verificar quais existem
    existing_docs = [doc for doc in deploy_docs if os.path.exists(doc)]
    
    if existing_docs:
        # Criar diretório docs se não existir
        os.makedirs('docs/old_deploy_guides', exist_ok=True)
        
        # Mover todos para pasta docs/old_deploy_guides exceto o DEPLOY_PYTHONANYWHERE.md principal
        for doc in existing_docs:
            if doc != 'DEPLOY_PYTHONANYWHERE.md':
                print(f"Movendo {doc} para docs/old_deploy_guides/")
                shutil.move(doc, f"docs/old_deploy_guides/{doc}")
        
        print_colored("Documentação de deploy organizada.", "green")
    
    # Mover relatórios e guias para pasta docs
    reports = [
        'RELATORIO_CORRECOES_TECHCARE.md',
        'RELATORIO_PROGRESSO_TECHCARE.md',
        'Relatório da Fase 2 de Correções e Melhorias - Projeto TechCare.md',
        'final_checks.md',
        'GUIA_EXECUCAO.md'
    ]
    
    os.makedirs('docs/reports', exist_ok=True)
    
    for report in reports:
        if os.path.exists(report):
            print(f"Movendo {report} para docs/reports/")
            shutil.move(report, f"docs/reports/{report}")
    
    print_colored("Relatórios organizados.", "green")

def clean_old_packages():
    """Remover pacotes de deploy antigos."""
    print_colored("Removendo pacotes de deploy antigos...", "blue")
    
    # Encontrar todos os pacotes de deploy exceto o mais recente
    deploy_packages = sorted(glob.glob("techcare_deploy_*.zip"), reverse=True)
    
    if len(deploy_packages) > 1:
        # Manter apenas o mais recente
        for package in deploy_packages[1:]:
            print(f"Removendo {package}")
            os.remove(package)
        
        print_colored(f"Pacote de deploy mantido: {deploy_packages[0]}", "green")
    elif len(deploy_packages) == 1:
        print_colored(f"Apenas um pacote de deploy encontrado: {deploy_packages[0]}", "green")
    else:
        print_colored("Nenhum pacote de deploy encontrado.", "yellow")

def update_gitignore():
    """Atualizar .gitignore para excluir arquivos desnecessários."""
    print_colored("Atualizando .gitignore...", "blue")
    
    gitignore_content = """# Arquivos específicos do Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Cobertura e relatórios de testes
.coverage
htmlcov/
tests/coverage_html/
.pytest_cache/
coverage.xml
*.cover

# Arquivos específicos do aplicativo
instance/
*.db
*.sqlite
*.sqlite3

# Ambiente virtual
venv/
env/
ENV/

# Logs e arquivos temporários
*.log
*.tmp
*.bak
*.swp
.DS_Store
Thumbs.db
resultado_testes*.txt

# Arquivos de IDE e editores
.idea/
.vscode/
*.sublime-project
*.sublime-workspace
.project
.pydevproject
.settings/

# Pacotes de deploy
techcare_deploy_*.zip
deploy_package/

# Outros
.env
node_modules/
"""
    
    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    
    print_colored(".gitignore atualizado com sucesso.", "green")

def create_deploy_package():
    """Criar pacote de deploy para o PythonAnywhere."""
    print_colored("Criando pacote de deploy atualizado...", "blue")
    
    try:
        # Verificar se o script existe
        if os.path.exists('create_deploy_package.py'):
            subprocess.run([sys.executable, 'create_deploy_package.py'])
            print_colored("Pacote de deploy criado com sucesso.", "green")
        else:
            print_colored("Script create_deploy_package.py não encontrado.", "yellow")
    except Exception as e:
        print_colored(f"Erro ao criar pacote de deploy: {str(e)}", "red")

def init_git_repo():
    """Inicializar ou atualizar repositório Git."""
    print_colored("Verificando repositório Git...", "blue")
    
    # Verificar se o Git está instalado
    try:
        subprocess.run(['git', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        print_colored("❌ Git não encontrado no sistema!", "red")
        print_colored("Foi criado um script 'install_git.py' para ajudar na instalação do Git.", "yellow")
        print_colored("Execute 'python install_git.py' para instalá-lo.", "yellow")
        print_colored("Após a instalação, reinicie o terminal/PowerShell e execute este script novamente.", "yellow")
        return False
    
    if not os.path.exists('.git'):
        print_colored("Inicializando repositório Git...", "yellow")
        subprocess.run(['git', 'init'])
        
        # Configurar usuário e email se fornecidos
        username = input("Digite seu nome de usuário Git (ou pressione Enter para pular): ")
        email = input("Digite seu email Git (ou pressione Enter para pular): ")
        
        if username:
            subprocess.run(['git', 'config', 'user.name', username])
        if email:
            subprocess.run(['git', 'config', 'user.email', email])
        
        print_colored("Repositório Git inicializado.", "green")
    else:
        print_colored("Repositório Git já existe.", "green")
    
    return True

def update_readme():
    """Atualizar o README.md com informações atualizadas do projeto."""
    print_colored("Atualizando README.md...", "blue")
    
    readme_content = """# TechCare - Sistema de Manutenção e Diagnóstico de Computadores

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
venv\\Scripts\\activate  # Windows
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
Última atualização: {}
""".format(datetime.datetime.now().strftime("%d/%m/%Y"))
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print_colored("README.md atualizado com sucesso.", "green")

def print_next_steps():
    """Imprimir próximos passos para o usuário."""
    print_colored("\n📋 PRÓXIMOS PASSOS RECOMENDADOS 📋", "cyan")
    
    # Verificar se o Git está instalado
    git_installed = False
    try:
        subprocess.run(['git', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        git_installed = True
    except (subprocess.SubprocessError, FileNotFoundError):
        git_installed = False
    
    # Verificar se o repositório git existe
    git_initialized = os.path.exists('.git')
    
    # Verificar se existe pacote de deploy
    deploy_packages = glob.glob("techcare_deploy_*.zip")
    has_deploy_package = len(deploy_packages) > 0
    
    # 1. Instalação do Git
    if not git_installed:
        print_colored("1. Instale o Git executando:", "yellow")
        print_colored("   python install_git.py", "cyan")
    
    # 2. Inicialização do Git
    if git_installed and not git_initialized:
        print_colored("1. Inicialize o repositório Git executando:", "yellow")
        print_colored("   python cleanup_project.py --git-init", "cyan")
    
    # 3. Criar pacote de deploy
    if not has_deploy_package:
        step_num = "1" if not (git_installed and not git_initialized) else "2"
        print_colored(f"{step_num}. Crie um pacote de deploy executando:", "yellow")
        print_colored("   python create_deploy_package.py", "cyan")
    
    # 4. Verificar pacote de deploy
    if has_deploy_package:
        step_num = "1"
        if not git_installed:
            step_num = "2"
        elif not git_initialized and git_installed:
            step_num = "2"
        
        print_colored(f"{step_num}. Verifique o pacote de deploy executando:", "yellow")
        print_colored("   python verify_package.py", "cyan")
        
        next_step = int(step_num) + 1
        print_colored(f"{next_step}. Configure o deploy para PythonAnywhere executando:", "yellow")
        print_colored("   python prepare_pythonanywhere_deploy.py", "cyan")
    
    # 5. Configurar o GitHub
    if git_installed and git_initialized:
        step_num = "1"
        if not git_installed:
            step_num = "2"
        elif has_deploy_package:
            step_num = "3"
        
        print_colored(f"{step_num}. Configure o repositório GitHub executando:", "yellow")
        print_colored("   python setup_github_repo.py", "cyan")
    
    # 6. Script principal
    print_colored("\nOu use o script unificado para todas as etapas:", "green")
    print_colored("   python prepare_project.py", "cyan")
    
    print_colored("\nPara mais detalhes sobre cada script, use o parâmetro --help:", "blue")
    print_colored("   python prepare_project.py --help", "cyan")

def main():
    # Analisar argumentos da linha de comando
    parser = argparse.ArgumentParser(description='Limpeza e preparação do projeto TechCare')
    parser.add_argument('--yes', '-y', action='store_true', help='Responder "sim" para todas as confirmações')
    parser.add_argument('--git-init', action='store_true', help='Inicializar repositório Git')
    parser.add_argument('--clean-cache', action='store_true', help='Limpar caches Python')
    parser.add_argument('--clean-temp', action='store_true', help='Remover arquivos temporários')
    parser.add_argument('--organize-docs', action='store_true', help='Organizar documentação')
    parser.add_argument('--clean-packages', action='store_true', help='Remover pacotes de deploy antigos')
    parser.add_argument('--update-gitignore', action='store_true', help='Atualizar .gitignore')
    parser.add_argument('--update-readme', action='store_true', help='Atualizar README.md')
    parser.add_argument('--create-package', action='store_true', help='Criar pacote de deploy')
    parser.add_argument('--all', action='store_true', help='Executar todas as tarefas')
    args = parser.parse_args()
    
    auto_yes = args.yes
    
    # Se nenhuma tarefa específica foi selecionada e não é --all, executa o fluxo interativo
    if not (args.git_init or args.clean_cache or args.clean_temp or args.organize_docs or 
            args.clean_packages or args.update_gitignore or args.update_readme or 
            args.create_package or args.all):
        
        print_colored("\n🧹 LIMPEZA E PREPARAÇÃO DO PROJETO TECHCARE 🚀\n", "cyan")
        
        # Limpar caches Python
        if get_confirmation("Deseja limpar caches Python (__pycache__ e .pyc)?", auto_yes):
            clean_pycache()
        
        # Limpar arquivos temporários
        if get_confirmation("Deseja remover arquivos temporários?", auto_yes):
            clean_temp_files()
        
        # Organizar documentação
        if get_confirmation("Deseja organizar arquivos de documentação?", auto_yes):
            clean_duplicate_docs()
        
        # Limpar pacotes antigos
        if get_confirmation("Deseja remover pacotes de deploy antigos?", auto_yes):
            clean_old_packages()
        
        # Atualizar .gitignore
        if get_confirmation("Deseja atualizar o arquivo .gitignore?", auto_yes):
            update_gitignore()
        
        # Atualizar README.md
        if get_confirmation("Deseja atualizar o README.md?", auto_yes):
            update_readme()
        
        # Criar pacote de deploy
        if get_confirmation("Deseja criar um novo pacote de deploy?", auto_yes):
            try:
                create_deploy_package()
            except Exception as e:
                print_colored(f"Erro ao criar pacote de deploy: {str(e)}", "red")
                print_colored("Você pode executar create_deploy_package.py separadamente depois.", "yellow")
        
        # Inicializar repositório Git
        if get_confirmation("Deseja inicializar/atualizar repositório Git?", auto_yes):
            try:
                init_git_repo()
            except Exception as e:
                print_colored(f"Erro ao inicializar repositório Git: {str(e)}", "red")
                print_colored("Você pode inicializar o Git manualmente mais tarde.", "yellow")
        
        print_colored("\n✅ LIMPEZA E PREPARAÇÃO CONCLUÍDAS! ✅\n", "green")
        print_colored("Seu projeto está pronto para deploy e compartilhamento no GitHub.", "green")
        
        # Perguntar se quer configurar GitHub
        if get_confirmation("Deseja configurar o repositório no GitHub agora?", auto_yes):
            try:
                remote_url = input("Digite a URL do repositório GitHub (ex: https://github.com/username/repo.git): ")
                if remote_url:
                    try:
                        subprocess.run(['git', 'remote', 'add', 'origin', remote_url])
                        print_colored("Remote 'origin' adicionado.", "green")
                        
                        if get_confirmation("Deseja fazer commit e push inicial?", auto_yes):
                            subprocess.run(['git', 'add', '.'])
                            commit_msg = input("Mensagem do commit (padrão: 'Commit inicial'): ") or "Commit inicial"
                            subprocess.run(['git', 'commit', '-m', commit_msg])
                            
                            # Perguntar sobre branch
                            branch = input("Nome da branch (padrão: 'main'): ") or "main"
                            subprocess.run(['git', 'branch', '-M', branch])
                            
                            # Solicitar credenciais para push
                            print_colored("\nPara fazer push para o GitHub, você precisará fornecer suas credenciais:", "yellow")
                            username = input("Digite seu nome de usuário GitHub: ")
                            
                            # Substitua o https:// padrão por https://username@
                            if remote_url.startswith('https://'):
                                remote_url = remote_url.replace('https://', f'https://{username}@')
                                subprocess.run(['git', 'remote', 'set-url', 'origin', remote_url])
                            
                            # Fazer push
                            subprocess.run(['git', 'push', '-u', 'origin', branch])
                            print_colored(f"Código enviado para o GitHub com sucesso na branch '{branch}'.", "green")
                    except Exception as e:
                        print_colored(f"Erro ao configurar GitHub: {str(e)}", "red")
            except Exception as e:
                print_colored(f"Erro ao configurar GitHub: {str(e)}", "red")
                print_colored("Você pode configurar o GitHub manualmente mais tarde.", "yellow")
    else:
        # Executa tarefas específicas com base nos argumentos
        print_colored("\n🧹 LIMPEZA E PREPARAÇÃO DO PROJETO TECHCARE (MODO AUTOMÁTICO) 🚀\n", "cyan")
        
        if args.all or args.clean_cache:
            print_colored("Limpando caches Python...", "blue")
            clean_pycache()
        
        if args.all or args.clean_temp:
            print_colored("Removendo arquivos temporários...", "blue")
            clean_temp_files()
        
        if args.all or args.organize_docs:
            print_colored("Organizando documentação...", "blue")
            clean_duplicate_docs()
        
        if args.all or args.clean_packages:
            print_colored("Removendo pacotes de deploy antigos...", "blue")
            clean_old_packages()
        
        if args.all or args.update_gitignore:
            print_colored("Atualizando .gitignore...", "blue")
            update_gitignore()
        
        if args.all or args.update_readme:
            print_colored("Atualizando README.md...", "blue")
            update_readme()
        
        if args.all or args.create_package:
            print_colored("Criando pacote de deploy...", "blue")
            try:
                create_deploy_package()
            except Exception as e:
                print_colored(f"Erro ao criar pacote de deploy: {str(e)}", "red")
        
        if args.all or args.git_init:
            print_colored("Inicializando repositório Git...", "blue")
            try:
                init_git_repo()
            except Exception as e:
                print_colored(f"Erro ao inicializar repositório Git: {str(e)}", "red")
    
    # Exibir próximos passos
    print_next_steps()
    
    print_colored("\n🎉 PROJETO TECHCARE PREPARADO COM SUCESSO! 🎉\n", "magenta")

if __name__ == "__main__":
    main() 