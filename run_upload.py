#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para executar o upload para o PythonAnywhere com os parâmetros já configurados
"""

import subprocess
import sys
import requests

def run_upload():
    username = "zewell10"
    token = "779aaf47f062a27fe9b56bd21b1830439be78d12"
    
    print(f"Verificando acesso à API do PythonAnywhere...")
    
    # Tente os dois hosts possíveis - a versão dos EUA e a versão da UE
    hosts = ["www.pythonanywhere.com", "eu.pythonanywhere.com"]
    working_host = None
    
    for host in hosts:
        url = f"https://{host}/api/v0/user/{username}/cpu/"
        headers = {'Authorization': f'Token {token}'}
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                print(f"✓ Conexão bem-sucedida com {host}")
                working_host = host
                break
            else:
                print(f"✗ Erro ao acessar {host}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"✗ Erro ao tentar conectar com {host}: {str(e)}")
    
    if not working_host:
        print("Não foi possível estabelecer conexão com nenhum host do PythonAnywhere.")
        return
    
    print(f"\nUsando host: {working_host}")
    
    # Agora podemos iniciar o upload com o host correto
    try:
        # Executando o comando
        cmd = ["python", "upload_to_pythonanywhere.py", "--username", username, "--token", token, "--host", working_host]
        print(f"Executando comando: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Exibindo a saída
        print("\nSAÍDA DO COMANDO:")
        print(result.stdout)
        
        # Exibindo erros, se houver
        if result.stderr:
            print("\nERROS:")
            print(result.stderr)
            
        print(f"\nCódigo de saída: {result.returncode}")
        
    except Exception as e:
        print(f"Erro ao executar o comando: {str(e)}")

if __name__ == "__main__":
    run_upload() 