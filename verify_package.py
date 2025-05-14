import os
import sys
import zipfile
import glob
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

def get_latest_package():
    """Encontrar o pacote de deploy mais recente."""
    packages = sorted(glob.glob("techcare_deploy_*.zip"), reverse=True)
    if not packages:
        return None
    return packages[0]

def list_required_files():
    """Listar arquivos essenciais que devem estar no pacote."""
    return [
        "app/__init__.py",
        "app/extensions.py",
        "app/models/*",
        "app/routes/*",
        "app/services/*",
        "app/templates/*",
        "app/static/*",
        "app/utils/*",
        "config.py",
        "requirements.txt",
        "requirements_pythonanywhere.txt",
        "requirements_pythonanywhere_fixed.txt",
        "wsgi.py",
        "wsgi_pythonanywhere.py",
        "DEPLOY_PYTHONANYWHERE.md",
        "fix_pandas_pythonanywhere.py",
        "README.md"
    ]

def check_files_in_package(package_path):
    """Verificar quais arquivos essenciais estão ou não no pacote."""
    if not os.path.exists(package_path):
        print_colored(f"O pacote {package_path} não foi encontrado!", "red")
        return False

    print_colored(f"\nAnalisando o pacote: {package_path}", "blue")
    
    # Arquivos necessários (com glob patterns)
    required_files = list_required_files()
    
    # Lista para armazenar arquivos que faltam
    missing_files = []
    
    # Ler conteúdo do zip
    try:
        with zipfile.ZipFile(package_path, 'r') as zip_ref:
            # Listar todos os arquivos no zip
            files_in_zip = zip_ref.namelist()
            
            # Verificar cada padrão de arquivo requerido
            for required_pattern in required_files:
                if "*" in required_pattern:
                    # Se for um padrão com wildcard, verifica se há pelo menos um arquivo correspondente
                    base_path = required_pattern.split("*")[0]
                    matching_files = [f for f in files_in_zip if f.startswith(base_path)]
                    
                    if not matching_files:
                        missing_files.append(required_pattern)
                else:
                    # Verificação direta de arquivo
                    if required_pattern not in files_in_zip:
                        missing_files.append(required_pattern)
    
            # Mostrar estatísticas
            print_colored(f"Total de arquivos no pacote: {len(files_in_zip)}", "blue")
            
            # Listar os 5 diretórios principais
            dirs = {}
            for file in files_in_zip:
                top_dir = file.split('/')[0] if '/' in file else 'root'
                dirs[top_dir] = dirs.get(top_dir, 0) + 1
            
            print_colored("\nDistribuição de arquivos por diretório:", "blue")
            for dir_name, count in sorted(dirs.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  {dir_name}: {count} arquivos")
            
            # Verificar se todos os arquivos requeridos estão presentes
            if missing_files:
                print_colored("\nArquivos essenciais que estão FALTANDO no pacote:", "red")
                for file in missing_files:
                    print(f"  - {file}")
                return False
            else:
                print_colored("\nTodos os arquivos essenciais estão presentes no pacote! ✅", "green")
                return True
                
    except Exception as e:
        print_colored(f"Erro ao verificar o pacote: {str(e)}", "red")
        return False

def check_package_freshness(package_path):
    """Verificar se o pacote foi criado recentemente."""
    if not os.path.exists(package_path):
        return False
    
    # Obter a data de modificação do arquivo
    mtime = os.path.getmtime(package_path)
    mod_time = datetime.datetime.fromtimestamp(mtime)
    now = datetime.datetime.now()
    
    # Calcular a diferença em dias
    days_diff = (now - mod_time).days
    
    print_colored(f"\nIdade do pacote:", "blue")
    if days_diff == 0:
        hours_diff = (now - mod_time).seconds // 3600
        if hours_diff == 0:
            mins_diff = (now - mod_time).seconds // 60
            print_colored(f"  Pacote criado há {mins_diff} minutos", "green")
        else:
            print_colored(f"  Pacote criado há {hours_diff} horas", "green")
    else:
        if days_diff < 2:
            print_colored(f"  Pacote criado há {days_diff} dia", "green")
        elif days_diff < 7:
            print_colored(f"  Pacote criado há {days_diff} dias", "yellow")
        else:
            print_colored(f"  Pacote criado há {days_diff} dias (recomendamos criar um novo pacote)", "red")
            return False
    
    return True

def check_package_size(package_path):
    """Verificar se o tamanho do pacote está dentro do esperado."""
    if not os.path.exists(package_path):
        return False
    
    # Obter o tamanho do arquivo em bytes
    size_bytes = os.path.getsize(package_path)
    size_mb = size_bytes / (1024 * 1024)
    
    print_colored(f"\nTamanho do pacote:", "blue")
    if size_mb < 0.5:
        print_colored(f"  {size_mb:.2f} MB (muito pequeno, pode estar faltando arquivos)", "red")
        return False
    elif size_mb > 50:
        print_colored(f"  {size_mb:.2f} MB (muito grande, pode conter arquivos desnecessários)", "yellow")
        return True
    else:
        print_colored(f"  {size_mb:.2f} MB (tamanho normal)", "green")
        return True

def main():
    print_colored("\n🔍 VERIFICAÇÃO DO PACOTE DE DEPLOY TECHCARE 📦\n", "cyan")
    
    # Encontrar o pacote mais recente
    latest_package = get_latest_package()
    
    if not latest_package:
        print_colored("Nenhum pacote de deploy encontrado!", "red")
        print_colored("Execute o script create_deploy_package.py para criar um novo pacote.", "yellow")
        return
    
    # Verificar o pacote
    files_ok = check_files_in_package(latest_package)
    freshness_ok = check_package_freshness(latest_package)
    size_ok = check_package_size(latest_package)
    
    # Resultado final
    print_colored("\nResultado da verificação:", "blue")
    if files_ok and freshness_ok and size_ok:
        print_colored("✅ O pacote está PRONTO para deploy!", "green")
    else:
        print_colored("❌ O pacote tem problemas que devem ser corrigidos antes do deploy!", "red")
        
        if not files_ok:
            print_colored("  - Arquivos essenciais faltando", "red")
        if not freshness_ok:
            print_colored("  - Pacote desatualizado", "red")
        if not size_ok:
            print_colored("  - Tamanho do pacote inadequado", "red")
            
        print_colored("\nRecomendações:", "yellow")
        print_colored("1. Execute o script cleanup_project.py para limpar o projeto", "yellow")
        print_colored("2. Execute o script create_deploy_package.py para criar um novo pacote", "yellow")
        print_colored("3. Execute este script novamente para verificar o novo pacote", "yellow")

if __name__ == "__main__":
    main() 