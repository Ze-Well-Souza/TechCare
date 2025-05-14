import os
import sys
import argparse
import requests
import getpass
import zipfile
import time
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

def check_latest_package():
    """Verifica se existe um pacote de deploy e se ele é recente."""
    import glob
    packages = sorted(glob.glob("techcare_deploy_*.zip"), reverse=True)
    
    if not packages:
        print_colored("Nenhum pacote de deploy encontrado!", "red")
        return None
    
    latest_package = packages[0]
    
    # Verificar a data de criação
    mtime = os.path.getmtime(latest_package)
    mod_time = datetime.datetime.fromtimestamp(mtime)
    now = datetime.datetime.now()
    days_diff = (now - mod_time).days
    
    if days_diff > 7:
        print_colored(f"O pacote mais recente ({latest_package}) foi criado há {days_diff} dias.", "yellow")
        if input("Deseja criar um novo pacote? (s/n): ").lower().startswith('s'):
            return None
    
    return latest_package

def create_new_package():
    """Criar um novo pacote de deploy."""
    print_colored("\nCriando novo pacote de deploy...", "blue")
    
    # Verificar se o script existe
    if os.path.exists('create_deploy_package.py'):
        import subprocess
        result = subprocess.run([sys.executable, 'create_deploy_package.py'], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Encontrar o nome do pacote criado na saída
            for line in result.stdout.splitlines():
                if "techcare_deploy_" in line and ".zip" in line:
                    package_name = line.split(":")[-1].strip()
                    print_colored(f"Pacote criado com sucesso: {package_name}", "green")
                    return package_name
        
        print_colored("Erro ao criar pacote:", "red")
        print(result.stderr)
        return None
    else:
        print_colored("Script create_deploy_package.py não encontrado!", "red")
        return None

def test_api_token(username, token):
    """Testar se o token da API do PythonAnywhere é válido."""
    url = f"https://www.pythonanywhere.com/api/v0/user/{username}/"
    headers = {"Authorization": f"Token {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print_colored("✅ Token da API válido!", "green")
            return True
        else:
            print_colored(f"❌ Token inválido (status code: {response.status_code})", "red")
            print_colored(f"Resposta: {response.text}", "red")
            return False
    except Exception as e:
        print_colored(f"❌ Erro ao testar token: {str(e)}", "red")
        return False

def upload_file_via_api(username, token, local_path, remote_path):
    """Upload de arquivo via API do PythonAnywhere."""
    url = f"https://www.pythonanywhere.com/api/v0/user/{username}/files/path{remote_path}"
    headers = {"Authorization": f"Token {token}"}
    
    with open(local_path, 'rb') as f:
        content = f.read()
    
    try:
        response = requests.post(url, headers=headers, files={"content": content})
        if response.status_code in (200, 201):
            return True
        else:
            print_colored(f"Erro ao fazer upload de {local_path}: {response.status_code} - {response.text}", "red")
            return False
    except Exception as e:
        print_colored(f"Exceção ao fazer upload de {local_path}: {str(e)}", "red")
        return False

def create_directory_via_api(username, token, path):
    """Criar diretório via API do PythonAnywhere."""
    url = f"https://www.pythonanywhere.com/api/v0/user/{username}/files/path{path}"
    headers = {"Authorization": f"Token {token}"}
    
    try:
        response = requests.post(url, headers=headers, json={"operation": "mkdir"})
        if response.status_code in (200, 201):
            return True
        else:
            print_colored(f"Erro ao criar diretório {path}: {response.status_code} - {response.text}", "red")
            return False
    except Exception as e:
        print_colored(f"Exceção ao criar diretório {path}: {str(e)}", "red")
        return False

def run_command_via_api(username, token, command):
    """Executar comando via API do PythonAnywhere."""
    url = f"https://www.pythonanywhere.com/api/v0/user/{username}/consoles/"
    headers = {"Authorization": f"Token {token}"}
    
    # Criar um console
    try:
        response = requests.post(url, headers=headers, json={"executable": "bash"})
        if response.status_code != 201:
            print_colored(f"Erro ao criar console: {response.status_code} - {response.text}", "red")
            return False
        
        console_id = response.json()["id"]
        
        # Executar o comando
        url = f"https://www.pythonanywhere.com/api/v0/user/{username}/consoles/{console_id}/send_input/"
        response = requests.post(url, headers=headers, data={"input": command + "\n"})
        
        if response.status_code != 200:
            print_colored(f"Erro ao executar comando: {response.status_code} - {response.text}", "red")
            return False
        
        print_colored(f"Comando executado: {command}", "green")
        return True
    except Exception as e:
        print_colored(f"Exceção ao executar comando: {str(e)}", "red")
        return False

def deploy_to_pythonanywhere(username, token, package_path, force=False):
    """Deploy do TechCare no PythonAnywhere."""
    print_colored("\n🚀 INICIANDO DEPLOY NO PYTHONANYWHERE 🚀", "cyan")
    
    if not test_api_token(username, token):
        return False
    
    # Definir caminhos
    remote_base_path = f"/home/{username}"
    remote_app_path = f"{remote_base_path}/TechCare"
    remote_package_path = f"{remote_base_path}/{os.path.basename(package_path)}"
    
    # 1. Upload do pacote
    print_colored(f"\n📤 Fazendo upload do pacote ({os.path.getsize(package_path)/1024/1024:.2f} MB)...", "blue")
    if not upload_file_via_api(username, token, package_path, remote_package_path):
        return False
    print_colored("✅ Upload do pacote concluído!", "green")
    
    # 2. Criar diretório de destino (se não existir)
    print_colored("\n📁 Verificando diretório de destino...", "blue")
    create_directory_via_api(username, token, remote_app_path)
    
    # 3. Extrair o pacote
    print_colored("\n📦 Extraindo pacote...", "blue")
    extract_cmd = f"cd {remote_base_path} && unzip -o {os.path.basename(package_path)} -d TechCare"
    if not run_command_via_api(username, token, extract_cmd):
        return False
    
    # 4. Configurar ambiente virtual
    print_colored("\n🔧 Configurando ambiente virtual...", "blue")
    setup_commands = [
        f"cd {remote_app_path}",
        "python3 -m venv venv || python -m venv venv",
        "source venv/bin/activate",
        "pip install --upgrade pip setuptools wheel",
        "python fix_pandas_pythonanywhere.py"
    ]
    
    for cmd in setup_commands:
        if not run_command_via_api(username, token, cmd):
            return False
    
    # 5. Criar/reconfigurar aplicação web via API
    print_colored("\n🌐 Configurando aplicação web...", "blue")
    print_colored("NOTA: Esta etapa requer configuração manual no painel do PythonAnywhere:", "yellow")
    print_colored("1. Acesse https://www.pythonanywhere.com/user/{}/webapps/".format(username), "yellow")
    print_colored("2. Se já existe uma aplicação, clique em 'Reload'", "yellow")
    print_colored("3. Se não existe, clique em 'Add a new web app':", "yellow")
    print_colored("   - Escolha o domínio (geralmente username.pythonanywhere.com)", "yellow")
    print_colored("   - Selecione 'Manual configuration'", "yellow")
    print_colored("   - Escolha 'Python 3.10'", "yellow")
    print_colored("   - Configure o caminho virtual: /home/{}/TechCare/venv".format(username), "yellow")
    print_colored("   - Configure o WSGI: use o conteúdo do arquivo wsgi_pythonanywhere.py", "yellow")
    print_colored("   - Configure os arquivos estáticos: URL: /static/, Directory: /home/{}/TechCare/app/static".format(username), "yellow")
    
    print_colored("\n✅ DEPLOY CONCLUÍDO! ✅", "green")
    print_colored(f"Acesse sua aplicação em: https://{username}.pythonanywhere.com", "green")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Deploy do TechCare no PythonAnywhere')
    parser.add_argument('--username', '-u', help='Nome de usuário do PythonAnywhere')
    parser.add_argument('--token', '-t', help='Token da API do PythonAnywhere')
    parser.add_argument('--force', '-f', action='store_true', help='Forçar criação de novo pacote')
    args = parser.parse_args()
    
    # Verificar nome de usuário
    username = args.username
    if not username:
        username = input("Digite seu nome de usuário do PythonAnywhere: ")
    
    # Verificar token
    token = args.token
    if not token:
        token = getpass.getpass("Digite seu token da API do PythonAnywhere: ")
    
    # Verificar pacote
    package_path = None
    if not args.force:
        package_path = check_latest_package()
    
    if not package_path:
        package_path = create_new_package()
        if not package_path:
            print_colored("Não foi possível criar um pacote de deploy. Abortando.", "red")
            return
    
    # Iniciar deploy
    deploy_to_pythonanywhere(username, token, package_path, args.force)

if __name__ == "__main__":
    main() 