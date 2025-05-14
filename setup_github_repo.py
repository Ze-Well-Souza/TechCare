import os
import sys
import subprocess
import argparse
import getpass
import json
import datetime
import webbrowser
import time
import platform

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

def check_git_installed():
    """Verificar se o Git está instalado."""
    try:
        subprocess.run(['git', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def get_git_config():
    """Obter configurações atuais do Git."""
    config = {}
    
    try:
        # Verificar se .git existe
        if not os.path.exists('.git'):
            return None
        
        # Obter user.name
        result = subprocess.run(['git', 'config', 'user.name'], capture_output=True, text=True)
        if result.returncode == 0:
            config['user_name'] = result.stdout.strip()
        
        # Obter user.email
        result = subprocess.run(['git', 'config', 'user.email'], capture_output=True, text=True)
        if result.returncode == 0:
            config['user_email'] = result.stdout.strip()
        
        # Obter remote.origin.url
        result = subprocess.run(['git', 'config', 'remote.origin.url'], capture_output=True, text=True)
        if result.returncode == 0:
            config['remote_url'] = result.stdout.strip()
        
        return config
    except Exception as e:
        print_colored(f"Erro ao obter configuração Git: {str(e)}", "red")
        return None

def check_github_credentials():
    """Verificar credenciais do GitHub."""
    try:
        # Testar conexão com GitHub
        result = subprocess.run(
            ['git', 'ls-remote', 'https://github.com/octocat/Hello-World.git', 'HEAD'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return result.returncode == 0
    except Exception:
        return False

def setup_credential_helper():
    """Configurar o credential helper para armazenar credenciais."""
    try:
        # No Windows, usar o manager-core
        if platform.system() == 'Windows':
            subprocess.run(['git', 'config', '--global', 'credential.helper', 'manager-core'])
        # No macOS, usar o osxkeychain
        elif platform.system() == 'Darwin':
            subprocess.run(['git', 'config', '--global', 'credential.helper', 'osxkeychain'])
        # No Linux, usar o cache
        else:
            subprocess.run(['git', 'config', '--global', 'credential.helper', 'cache --timeout=3600'])
        
        print_colored("✅ Credential helper configurado com sucesso.", "green")
        return True
    except Exception as e:
        print_colored(f"❌ Erro ao configurar credential helper: {str(e)}", "red")
        return False

def init_git_repo():
    """Inicializar repositório Git se ainda não existir."""
    if not os.path.exists('.git'):
        try:
            print_colored("Inicializando repositório Git...", "blue")
            subprocess.run(['git', 'init'])
            print_colored("✅ Repositório Git inicializado com sucesso!", "green")
            return True
        except Exception as e:
            print_colored(f"❌ Erro ao inicializar repositório Git: {str(e)}", "red")
            return False
    else:
        print_colored("✅ Repositório Git já inicializado.", "green")
        return True

def configure_git_user():
    """Configurar usuário e email do Git."""
    git_config = get_git_config()
    
    # Verificar se já existe configuração
    if git_config and 'user_name' in git_config and 'user_email' in git_config:
        print_colored(f"Configuração atual:", "blue")
        print_colored(f"Nome: {git_config['user_name']}", "cyan")
        print_colored(f"Email: {git_config['user_email']}", "cyan")
        
        if not get_confirmation("Deseja alterar estas configurações?"):
            return True
    
    try:
        # Coletar informações do usuário
        print_colored("\nConfigurando usuário Git:", "blue")
        user_name = input("Digite seu nome completo (ex: João Silva): ")
        user_email = input("Digite seu email (ex: joao@exemplo.com): ")
        
        if user_name and user_email:
            # Configurar usuário e email
            subprocess.run(['git', 'config', '--global', 'user.name', user_name])
            subprocess.run(['git', 'config', '--global', 'user.email', user_email])
            print_colored("✅ Usuário Git configurado com sucesso!", "green")
            return True
        else:
            print_colored("⚠️ Nome ou email não fornecidos. Mantendo configuração atual.", "yellow")
            return False
    except Exception as e:
        print_colored(f"❌ Erro ao configurar usuário Git: {str(e)}", "red")
        return False

def create_github_repo(username, token=None, repo_name="techcare", description="Sistema de Manutenção e Diagnóstico de Computadores", private=False):
    """Criar repositório no GitHub via API."""
    try:
        import requests
        
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"token {token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        data = {
            "name": repo_name,
            "description": description,
            "private": private,
            "auto_init": False
        }
        
        response = requests.post("https://api.github.com/user/repos", headers=headers, json=data)
        
        if response.status_code in (201, 200):
            print_colored("✅ Repositório criado com sucesso no GitHub!", "green")
            repo_info = response.json()
            return repo_info["html_url"], repo_info["clone_url"]
        else:
            print_colored(f"❌ Erro ao criar repositório: {response.status_code}", "red")
            print_colored(response.text, "red")
            return None, None
    
    except ImportError:
        print_colored("O módulo 'requests' não está instalado.", "yellow")
        print_colored("O repositório precisará ser criado manualmente.", "yellow")
        return None, None
    except Exception as e:
        print_colored(f"❌ Erro ao criar repositório: {str(e)}", "red")
        return None, None

def setup_github_repo():
    """Configurar repositório GitHub."""
    print_colored("\n🚀 CONFIGURAÇÃO DO REPOSITÓRIO GITHUB 🚀\n", "cyan")
    
    # Verificar se o Git está instalado
    if not check_git_installed():
        print_colored("❌ Git não está instalado!", "red")
        print_colored("Execute 'python install_git.py' primeiro.", "yellow")
        return False
    
    # Inicializar repositório Git
    if not init_git_repo():
        return False
    
    # Configurar usuário Git
    configure_git_user()
    
    # Configurar credential helper
    setup_credential_helper()
    
    # Verificar se já existe um remote
    git_config = get_git_config()
    if git_config and 'remote_url' in git_config:
        print_colored(f"Repositório remoto atual: {git_config['remote_url']}", "blue")
        if not get_confirmation("Deseja reconfigurá-lo?"):
            # Perguntar se quer fazer commit e push
            if get_confirmation("Deseja fazer commit e push das alterações?"):
                commit_and_push()
            return True
    
    # Solicitar informações para configurar GitHub
    print_colored("\nExistem duas formas de continuar:", "blue")
    print_colored("1. Criar um novo repositório no GitHub", "yellow")
    print_colored("2. Conectar a um repositório existente", "yellow")
    
    choice = input("\nEscolha uma opção (1 ou 2): ")
    
    if choice == '1':
        # Tentar criar repositório via API
        print_colored("\nPara criar automaticamente um repositório no GitHub, precisamos de um token de acesso pessoal.", "blue")
        print_colored("Você pode criar um token em: https://github.com/settings/tokens", "blue")
        print_colored("Este token deve ter permissão para 'repo' (acesso completo aos repositórios privados e públicos).", "blue")
        
        if get_confirmation("Deseja criar um token agora e continuar?"):
            webbrowser.open("https://github.com/settings/tokens/new?scopes=repo&description=TechCare%20Setup")
            print_colored("\nApós criar o token, copie-o e cole aqui.", "blue")
            
            github_username = input("Digite seu nome de usuário GitHub: ")
            github_token = getpass.getpass("Cole seu token de acesso pessoal: ")
            
            if github_username and github_token:
                # Nome do repositório
                repo_name = input("Nome do repositório (padrão: techcare): ") or "techcare"
                # Descrição
                description = input("Descrição (padrão: Sistema de Manutenção e Diagnóstico de Computadores): ") or "Sistema de Manutenção e Diagnóstico de Computadores"
                # Privado ou público
                is_private = get_confirmation("Deseja que o repositório seja privado?")
                
                # Criar repositório
                repo_url, clone_url = create_github_repo(
                    username=github_username,
                    token=github_token,
                    repo_name=repo_name,
                    description=description,
                    private=is_private
                )
                
                if clone_url:
                    try:
                        # Adicionar remote
                        subprocess.run(['git', 'remote', 'add', 'origin', clone_url])
                        print_colored(f"✅ Remote 'origin' configurado: {clone_url}", "green")
                        
                        # Fazer commit e push inicial
                        if get_confirmation("Deseja fazer o commit e push inicial?"):
                            commit_and_push()
                        
                        return True
                    except Exception as e:
                        print_colored(f"❌ Erro ao configurar remote: {str(e)}", "red")
                        return False
            else:
                print_colored("⚠️ Usuário ou token não fornecidos.", "yellow")
        
        # Se falhar a criação automática, continuar com criação manual
        print_colored("\nAcesse o GitHub e crie manualmente um novo repositório:", "blue")
        print_colored("1. Acesse https://github.com/new", "cyan")
        print_colored("2. Preencha o nome e descrição", "cyan")
        print_colored("3. Escolha a visibilidade (público ou privado)", "cyan")
        print_colored("4. NÃO inicialize com README", "cyan")
        print_colored("5. Clique em 'Create repository'", "cyan")
        
        webbrowser.open("https://github.com/new")
        
        input("\nPressione Enter após criar o repositório...")
    
    # Conectar a um repositório existente
    print_colored("\nAgora vamos conectar ao repositório GitHub:", "blue")
    github_url = input("Cole a URL do repositório (ex: https://github.com/usuario/techcare.git): ")
    
    if not github_url:
        print_colored("❌ URL não fornecida. Cancelando.", "red")
        return False
    
    try:
        # Adicionar ou atualizar remote
        if git_config and 'remote_url' in git_config:
            subprocess.run(['git', 'remote', 'set-url', 'origin', github_url])
            print_colored(f"✅ Remote 'origin' atualizado: {github_url}", "green")
        else:
            subprocess.run(['git', 'remote', 'add', 'origin', github_url])
            print_colored(f"✅ Remote 'origin' adicionado: {github_url}", "green")
        
        # Fazer commit e push inicial
        if get_confirmation("Deseja fazer o commit e push inicial?"):
            commit_and_push()
        
        return True
    except Exception as e:
        print_colored(f"❌ Erro ao configurar remote: {str(e)}", "red")
        return False

def commit_and_push():
    """Fazer commit e push para o GitHub."""
    try:
        # Verificar status
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        
        # Se não há nada para commitar
        if not result.stdout.strip():
            print_colored("⚠️ Não há alterações para commitar.", "yellow")
            
            # Verificar se há commits locais para enviar
            result = subprocess.run(['git', 'log', '--branches', '--not', '--remotes', '--oneline'], capture_output=True, text=True)
            if not result.stdout.strip():
                print_colored("⚠️ Não há commits locais para enviar ao GitHub.", "yellow")
                return True
            
            # Se há commits locais, perguntar se quer fazer push
            if get_confirmation("Há commits locais não enviados. Deseja enviar agora?"):
                # Escolher branch
                branch = input("Nome da branch (padrão: main): ") or "main"
                
                # Renomear branch se necessário
                subprocess.run(['git', 'branch', '-M', branch])
                
                # Push
                subprocess.run(['git', 'push', '-u', 'origin', branch])
                print_colored(f"✅ Código enviado para o GitHub na branch '{branch}'.", "green")
                print_colored(f"👉 Verifique em: {get_github_url()}", "cyan")
                return True
            
            return True
        
        # Adicionar tudo ao stage
        print_colored("\nAdicionando arquivos ao stage...", "blue")
        subprocess.run(['git', 'add', '.'])
        
        # Fazer commit
        commit_msg = input("\nDigite a mensagem do commit (padrão: Commit inicial do TechCare): ") or "Commit inicial do TechCare"
        subprocess.run(['git', 'commit', '-m', commit_msg])
        print_colored("✅ Commit realizado com sucesso!", "green")
        
        # Escolher branch
        branch = input("\nNome da branch (padrão: main): ") or "main"
        
        # Renomear branch se necessário
        subprocess.run(['git', 'branch', '-M', branch])
        
        # Push
        print_colored(f"\nEnviando código para o GitHub na branch '{branch}'...", "blue")
        print_colored("Caso seja solicitado, insira suas credenciais do GitHub.", "yellow")
        
        push_process = subprocess.run(['git', 'push', '-u', 'origin', branch], capture_output=True, text=True)
        
        if push_process.returncode == 0:
            print_colored(f"✅ Código enviado para o GitHub com sucesso na branch '{branch}'.", "green")
            print_colored(f"👉 Verifique em: {get_github_url()}", "cyan")
            return True
        else:
            print_colored("❌ Erro ao enviar código para o GitHub:", "red")
            print_colored(push_process.stderr, "red")
            
            # Verificar se é erro de autenticação
            if "Authentication failed" in push_process.stderr:
                print_colored("\nProblema de autenticação detectado!", "yellow")
                handle_authentication_error()
            
            return False
    
    except Exception as e:
        print_colored(f"❌ Erro ao commitar e enviar código: {str(e)}", "red")
        return False

def get_github_url():
    """Obter a URL do repositório GitHub."""
    try:
        result = subprocess.run(['git', 'config', '--get', 'remote.origin.url'], capture_output=True, text=True)
        
        if result.returncode == 0:
            url = result.stdout.strip()
            # Converter URL SSH para HTTPS se necessário
            if url.startswith('git@github.com:'):
                url = url.replace('git@github.com:', 'https://github.com/')
            # Remover .git do final
            if url.endswith('.git'):
                url = url[:-4]
            return url
    except Exception:
        pass
    
    return "https://github.com"

def handle_authentication_error():
    """Tratar erro de autenticação do GitHub."""
    print_colored("\n🔒 ERRO DE AUTENTICAÇÃO DO GITHUB 🔒\n", "magenta")
    print_colored("Existem algumas razões comuns para problemas de autenticação:", "blue")
    print_colored("1. Senha incorreta", "yellow")
    print_colored("2. Autenticação de dois fatores (2FA) ativada no GitHub", "yellow")
    print_colored("3. Token de acesso pessoal expirado ou inválido", "yellow")
    
    print_colored("\nComo resolver:", "blue")
    print_colored("1. Se você usa 2FA, você DEVE usar um token de acesso pessoal em vez da senha", "cyan")
    print_colored("2. Você pode criar um novo token em: https://github.com/settings/tokens", "cyan")
    print_colored("3. Use o token como senha quando solicitado", "cyan")
    
    if get_confirmation("\nDeseja abrir a página para criar um token?"):
        webbrowser.open("https://github.com/settings/tokens/new?scopes=repo&description=TechCare%20Access")
        print_colored("\nApós criar o token, tente fazer o push novamente usando o token como senha.", "cyan")
    
    print_colored("\nComo atualizar suas credenciais:", "blue")
    
    # Configurar o credential helper
    setup_credential_helper()
    
    # Instruções adicionais dependendo do sistema
    system = platform.system()
    if system == 'Windows':
        print_colored("No Windows, você pode gerenciar as credenciais em:", "cyan")
        print_colored("Painel de Controle > Contas de Usuário > Gerenciador de Credenciais > Credenciais do Windows", "cyan")
        print_colored("Procure por 'git:https://github.com' e remova-o, ou edite e atualize suas credenciais.", "cyan")
        
        if get_confirmation("\nDeseja abrir o Gerenciador de Credenciais?"):
            subprocess.run(['control', 'keymgr.dll'])

def print_help():
    """Exibir ajuda sobre o script."""
    print_colored("\n📚 AJUDA DO SCRIPT DE CONFIGURAÇÃO DO GITHUB 📚\n", "cyan")
    print_colored("Este script facilita a integração do projeto TechCare com o GitHub.", "blue")
    print_colored("Ele ajuda a:", "blue")
    print_colored("- Inicializar um repositório Git local", "cyan")
    print_colored("- Configurar o usuário e email do Git", "cyan")
    print_colored("- Criar ou conectar-se a um repositório no GitHub", "cyan")
    print_colored("- Fazer o primeiro commit e push", "cyan")
    print_colored("- Resolver problemas comuns de autenticação", "cyan")
    
    print_colored("\nArgumentos disponíveis:", "blue")
    print_colored("--help, -h       : Exibe esta ajuda", "cyan")
    print_colored("--yes, -y        : Responde 'sim' para todas as confirmações", "cyan")
    print_colored("--init-only      : Apenas inicializa o repositório Git local", "cyan")
    print_colored("--push-only      : Apenas faz commit e push das alterações", "cyan")
    
    print_colored("\nExemplos de uso:", "blue")
    print_colored("python setup_github_repo.py            : Execução interativa completa", "cyan")
    print_colored("python setup_github_repo.py --yes      : Execução com confirmações automáticas", "cyan")
    print_colored("python setup_github_repo.py --init-only: Apenas inicializa o Git", "cyan")
    print_colored("python setup_github_repo.py --push-only: Apenas faz commit e push", "cyan")

def main():
    # Analisar argumentos da linha de comando
    parser = argparse.ArgumentParser(description='Configuração e compartilhamento do repositório no GitHub')
    parser.add_argument('--yes', '-y', action='store_true', help='Responder "sim" para todas as confirmações')
    parser.add_argument('--init-only', action='store_true', help='Apenas inicializar o repositório Git local')
    parser.add_argument('--push-only', action='store_true', help='Apenas fazer commit e push das alterações')
    args = parser.parse_args()
    
    if len(sys.argv) > 1 and (sys.argv[1] == '--help' or sys.argv[1] == '-h'):
        print_help()
        return
    
    if args.init_only:
        if check_git_installed():
            init_git_repo()
            configure_git_user()
        else:
            print_colored("❌ Git não está instalado!", "red")
            print_colored("Execute 'python install_git.py' primeiro.", "yellow")
    elif args.push_only:
        if check_git_installed():
            if os.path.exists('.git'):
                commit_and_push()
            else:
                print_colored("❌ Este diretório não é um repositório Git.", "red")
                print_colored("Execute 'git init' ou 'python setup_github_repo.py --init-only' primeiro.", "yellow")
        else:
            print_colored("❌ Git não está instalado!", "red")
            print_colored("Execute 'python install_git.py' primeiro.", "yellow")
    else:
        setup_github_repo()
    
    print_colored("\n🎉 CONFIGURAÇÃO GIT/GITHUB CONCLUÍDA! 🎉\n", "magenta")

if __name__ == "__main__":
    main() 