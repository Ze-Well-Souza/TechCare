import os
import sys
import subprocess
import argparse
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

def get_confirmation(message):
    """Solicitar confirmação do usuário."""
    response = input(f"{message} (s/n): ").lower()
    return response.startswith('s')

def run_script(script_name, args=None):
    """Executar um script Python."""
    if not os.path.exists(script_name):
        print_colored(f"Script {script_name} não encontrado!", "red")
        return False
    
    cmd = [sys.executable, script_name]
    if args:
        cmd.extend(args)
    
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError:
        return False

def main():
    parser = argparse.ArgumentParser(description='Preparação completa do projeto TechCare')
    parser.add_argument('--clean-only', action='store_true', help='Executar apenas a limpeza')
    parser.add_argument('--verify-only', action='store_true', help='Verificar apenas o pacote de deploy')
    parser.add_argument('--github-only', action='store_true', help='Configurar apenas o repositório GitHub')
    parser.add_argument('--deploy-only', action='store_true', help='Preparar apenas o deploy para PythonAnywhere')
    parser.add_argument('--github-token', help='Token de acesso pessoal do GitHub')
    parser.add_argument('--github-repo', help='Nome do repositório GitHub')
    parser.add_argument('--pythonanywhere-user', help='Nome de usuário do PythonAnywhere')
    parser.add_argument('--pythonanywhere-token', help='Token da API do PythonAnywhere')
    args = parser.parse_args()

    print_colored("\n🚀 PREPARAÇÃO COMPLETA DO PROJETO TECHCARE 🚀\n", "cyan")
    print_colored(f"Data/Hora: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", "cyan")
    print_colored("=" * 60, "cyan")
    
    # Verificar scripts necessários
    required_scripts = {
        'cleanup_project.py': "Limpeza do projeto",
        'verify_package.py': "Verificação do pacote de deploy",
        'setup_github_repo.py': "Configuração do GitHub",
        'prepare_pythonanywhere_deploy.py': "Deploy no PythonAnywhere"
    }
    
    missing_scripts = []
    for script, desc in required_scripts.items():
        if not os.path.exists(script):
            missing_scripts.append(script)
    
    if missing_scripts:
        print_colored("⚠️ Os seguintes scripts necessários não foram encontrados:", "yellow")
        for script in missing_scripts:
            print_colored(f"  - {script}", "yellow")
        
        if not get_confirmation("Deseja continuar mesmo assim?"):
            print_colored("Processo cancelado pelo usuário.", "red")
            return
    
    # Etapa 1: Limpeza do projeto
    if args.clean_only or not (args.verify_only or args.github_only or args.deploy_only):
        print_colored("\n🧹 ETAPA 1: LIMPEZA DO PROJETO 🧹", "blue")
        
        if os.path.exists('cleanup_project.py'):
            if run_script('cleanup_project.py'):
                print_colored("✅ Limpeza do projeto concluída com sucesso!", "green")
            else:
                print_colored("❌ Ocorreram erros durante a limpeza do projeto.", "red")
                if not get_confirmation("Deseja continuar mesmo assim?"):
                    return
        else:
            print_colored("❌ Script de limpeza não encontrado.", "red")
            if not get_confirmation("Deseja continuar sem executar a limpeza?"):
                return
    
    # Etapa 2: Verificação do pacote de deploy
    if args.verify_only or not (args.clean_only or args.github_only or args.deploy_only):
        print_colored("\n📦 ETAPA 2: VERIFICAÇÃO DO PACOTE DE DEPLOY 📦", "blue")
        
        if os.path.exists('verify_package.py'):
            if run_script('verify_package.py'):
                print_colored("✅ Verificação do pacote concluída!", "green")
            else:
                print_colored("⚠️ O pacote pode ter problemas.", "yellow")
                if not get_confirmation("Deseja continuar mesmo assim?"):
                    return
        else:
            print_colored("❌ Script de verificação não encontrado.", "red")
            if not get_confirmation("Deseja continuar sem verificar o pacote?"):
                return
    
    # Etapa 3: Configuração do GitHub
    if args.github_only or not (args.clean_only or args.verify_only or args.deploy_only):
        print_colored("\n🌐 ETAPA 3: CONFIGURAÇÃO DO GITHUB 🌐", "blue")
        
        if os.path.exists('setup_github_repo.py'):
            github_args = []
            
            if args.github_token:
                github_args.extend(['--token', args.github_token])
            
            if args.github_repo:
                github_args.extend(['--repo', args.github_repo])
            
            if run_script('setup_github_repo.py', github_args):
                print_colored("✅ Configuração do GitHub concluída!", "green")
            else:
                print_colored("⚠️ Ocorreram problemas na configuração do GitHub.", "yellow")
                if not get_confirmation("Deseja continuar mesmo assim?"):
                    return
        else:
            print_colored("❌ Script de configuração do GitHub não encontrado.", "red")
            if not get_confirmation("Deseja continuar sem configurar o GitHub?"):
                return
    
    # Etapa 4: Preparação para deploy no PythonAnywhere
    if args.deploy_only or not (args.clean_only or args.verify_only or args.github_only):
        print_colored("\n🚀 ETAPA 4: PREPARAÇÃO PARA DEPLOY NO PYTHONANYWHERE 🚀", "blue")
        
        if os.path.exists('prepare_pythonanywhere_deploy.py'):
            pythonanywhere_args = []
            
            if args.pythonanywhere_user:
                pythonanywhere_args.extend(['--username', args.pythonanywhere_user])
            
            if args.pythonanywhere_token:
                pythonanywhere_args.extend(['--token', args.pythonanywhere_token])
            
            if get_confirmation("Deseja preparar o projeto para deploy no PythonAnywhere?"):
                if run_script('prepare_pythonanywhere_deploy.py', pythonanywhere_args):
                    print_colored("✅ Preparação para deploy concluída!", "green")
                else:
                    print_colored("⚠️ Ocorreram problemas na preparação para deploy.", "yellow")
            else:
                print_colored("⏩ Etapa de deploy ignorada pelo usuário.", "yellow")
        else:
            print_colored("❌ Script de preparação para deploy não encontrado.", "red")
            if get_confirmation("Deseja continuar sem preparar o deploy?"):
                print_colored("⏩ Etapa de deploy ignorada.", "yellow")
            else:
                return
    
    print_colored("\n✅ PROCESSO DE PREPARAÇÃO CONCLUÍDO! ✅\n", "green")
    print_colored("O projeto TechCare está pronto para ser compartilhado e implantado.", "green")
    print_colored("=" * 60, "cyan")

if __name__ == "__main__":
    main() 