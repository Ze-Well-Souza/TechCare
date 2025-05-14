import os
import sys
import subprocess
import webbrowser
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

def check_git_installed():
    """Verificar se o Git está instalado."""
    try:
        subprocess.run(['git', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def install_git_windows():
    """Ajudar o usuário a instalar o Git no Windows."""
    print_colored("\n🚀 INSTALAÇÃO DO GIT NO WINDOWS 🚀\n", "cyan")
    
    if check_git_installed():
        print_colored("✅ Git já está instalado no seu sistema!", "green")
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print_colored(f"Versão: {result.stdout.strip()}", "green")
        return True
    
    print_colored("❌ Git não está instalado no seu sistema.", "red")
    print_colored("\nOpções para instalar o Git:", "blue")
    print_colored("1. Baixar e instalar o Git diretamente (recomendado)", "yellow")
    print_colored("2. Usar o chocolatey para instalar o Git (requer privilégios de administrador)", "yellow")
    print_colored("3. Sair sem instalar", "yellow")
    
    choice = input("\nEscolha uma opção (1-3): ")
    
    if choice == '1':
        # Abrir página de download do Git
        print_colored("\nAbrindo página de download do Git...", "blue")
        webbrowser.open("https://git-scm.com/download/win")
        
        print_colored("\nInstruções:", "magenta")
        print_colored("1. Baixe a versão adequada para seu sistema (32 ou 64 bits)", "cyan")
        print_colored("2. Execute o instalador", "cyan")
        print_colored("3. Aceite as configurações padrão (recomendado)", "cyan")
        print_colored("4. Na tela 'Adjusting your PATH environment', selecione:", "cyan")
        print_colored("   'Git from the command line and also from 3rd-party software'", "cyan")
        print_colored("5. Complete a instalação", "cyan")
        print_colored("6. Feche e reabra o PowerShell/CMD após a instalação", "cyan")
        print_colored("7. Execute novamente este script para verificar a instalação", "cyan")
        
        return False
    
    elif choice == '2':
        # Instalar via Chocolatey
        print_colored("\nTentando instalar o Git via Chocolatey...", "blue")
        
        # Verificar se o Chocolatey está instalado
        try:
            subprocess.run(['choco', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            print_colored("Chocolatey encontrado. Instalando Git...", "green")
            
            # Instalar Git
            try:
                subprocess.run(['choco', 'install', 'git', '-y'], check=True)
                print_colored("\n✅ Git instalado com sucesso via Chocolatey!", "green")
                print_colored("Por favor, feche e reabra o PowerShell/CMD para que as alterações tenham efeito.", "yellow")
                return False
            except subprocess.CalledProcessError:
                print_colored("❌ Falha ao instalar o Git via Chocolatey.", "red")
                print_colored("   Tente a opção 1 (download manual) ou execute o PowerShell como administrador.", "yellow")
                return False
        
        except (subprocess.SubprocessError, FileNotFoundError):
            print_colored("❌ Chocolatey não está instalado.", "red")
            print_colored("\nDeseja instalar o Chocolatey primeiro? (s/n): ", "yellow")
            if input().lower().startswith('s'):
                print_colored("\nPara instalar o Chocolatey, execute o PowerShell como administrador e digite:", "magenta")
                print_colored('Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString(\'https://community.chocolatey.org/install.ps1\'))', "cyan")
                print_colored("\nDepois de instalar o Chocolatey, execute este script novamente.", "magenta")
            else:
                print_colored("Tente a opção 1 (download manual) ou execute o PowerShell como administrador.", "yellow")
            
            return False
    
    else:
        print_colored("\nInstalação do Git cancelada.", "yellow")
        return False

def main():
    system = platform.system()
    
    if system == "Windows":
        install_git_windows()
    else:
        print_colored(f"Este script é destinado para Windows. Seu sistema é: {system}", "yellow")
        print_colored("Para instalar o Git em outros sistemas:", "blue")
        
        if system == "Linux":
            print_colored("Linux (Ubuntu/Debian): sudo apt-get install git", "cyan")
            print_colored("Linux (Fedora): sudo dnf install git", "cyan")
            print_colored("Linux (Arch): sudo pacman -S git", "cyan")
        elif system == "Darwin":  # macOS
            print_colored("macOS: brew install git (requer Homebrew)", "cyan")
            print_colored("ou baixe do site oficial: https://git-scm.com/download/mac", "cyan")
        
        print_colored("\nOu visite: https://git-scm.com/downloads", "blue")

if __name__ == "__main__":
    main() 