5#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import platform

def clear_screen():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def run_tests(marker=None):
    base_command = ['pytest']
    
    if marker:
        base_command.extend(['-m', marker])
    
    project_path = os.path.dirname(os.path.abspath(__file__))
    env = os.environ.copy()
    env['PYTHONPATH'] = project_path
    
    try:
        result = subprocess.run(base_command, env=env, check=True)
        print(f'Testes {marker or "gerais"} executados com sucesso!')
        return 0
    except subprocess.CalledProcessError as e:
        print(f'Erro ao executar testes: {e}')
        return 1

def main():
    clear_screen()
    
    markers = {
        '1': 'unit',
        '2': 'integration', 
        '3': 'security', 
        '4': 'performance',
        '5': None  # Todos os testes
    }
    
    # Verificar se há argumentos na linha de comando
    if len(sys.argv) > 1 and sys.argv[1] in markers:
        choice = sys.argv[1]
    else:
        print('== TechCare - Execucao de Testes Automatizados ==')
        print('Selecione o tipo de teste:')
        print('1. Testes Unitarios')
        print('2. Testes de Integracao')
        print('3. Testes de Seguranca')
        print('4. Testes de Performance')
        print('5. Todos os Testes')
        
        choice = input('Digite o numero da opcao: ')
    
    if choice == '5':
        sys.exit(run_tests())
    elif choice in markers:
        sys.exit(run_tests(markers[choice]))
    else:
        print('Opcao invalida!')
        sys.exit(1)

if __name__ == '__main__':
    main()
