#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para iniciar a aplicação TechCare localmente.

Este script inicia a aplicação TechCare com configurações adaptativas,
resolvendo problemas de conflitos de dependências e tratando diferenças
entre sistemas operacionais.
"""

import os
import sys
import logging
import argparse
import platform
import importlib.util
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse os argumentos da linha de comando"""
    parser = argparse.ArgumentParser(description='Iniciar a aplicação TechCare localmente')
    parser.add_argument('--host', default='127.0.0.1', help='Host para executar o servidor (padrão: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5000, help='Porta para executar o servidor (padrão: 5000)')
    parser.add_argument('--debug', action='store_true', help='Ativar modo de depuração')
    parser.add_argument('--env', default='development', 
                       choices=['development', 'testing', 'production'], 
                       help='Ambiente de execução (padrão: development)')
    parser.add_argument('--diagnostic', action='store_true',
                       help='Executar apenas o diagnóstico do sistema sem iniciar o servidor web')
    return parser.parse_args()

def verify_dependencies():
    """Verifica se as dependências necessárias estão instaladas"""
    required_modules = ['flask', 'sqlalchemy', 'flask_login']
    missing_modules = []
    
    for module in required_modules:
        if importlib.util.find_spec(module) is None:
            missing_modules.append(module)
    
    if missing_modules:
        logger.error(f"Dependências ausentes: {', '.join(missing_modules)}")
        logger.error("Execute 'python setup_local_env.py' para instalar as dependências necessárias.")
        return False
    
    logger.info("Todas as dependências básicas estão presentes.")
    return True

def setup_environment(args):
    """Configura o ambiente de execução"""
    # Configura variáveis de ambiente
    os.environ['FLASK_ENV'] = args.env
    os.environ['FLASK_CONFIG'] = args.env
    
    if args.debug:
        os.environ['FLASK_DEBUG'] = '1'
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Modo de depuração ativado.")
    
    # Verifica se estamos em um ambiente virtual
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if not in_venv:
        logger.warning("Atenção: Você não está em um ambiente virtual Python.")
        logger.warning("Para melhores resultados, execute 'python setup_local_env.py' primeiro.")
    
    # Detecta o sistema operacional
    is_windows = sys.platform.startswith('win')
    if is_windows:
        logger.info(f"Sistema Windows detectado: {platform.platform()}")
    else:
        logger.info(f"Sistema não-Windows detectado: {platform.platform()}")
        
    # Cria pastas de dados necessárias
    data_paths = [
        Path('instance/data'),
        Path('instance/data/diagnostics'),
        Path('instance/data/repair_logs'),
        Path('instance/diagnostics')
    ]
    
    for path in data_paths:
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Diretório criado/verificado: {path}")

    return True

def run_app(args):
    """Executa a aplicação Flask"""
    try:
        # Tentamos importar a aplicação primeiro
        # Se falhar, provavelmente há um problema de importação de módulos
        logger.info("Inicializando a aplicação...")
        from app import create_app
        
        # Cria a aplicação Flask
        app = create_app(args.env)
        
        # Cria pastas adicionais com base na configuração da aplicação
        os.makedirs(os.path.join(app.config.get('DIAGNOSTIC_SAVE_PATH', 'instance/diagnostics')), exist_ok=True)
        os.makedirs(os.path.join(app.config.get('REPAIR_LOGS_PATH', 'instance/repair_logs')), exist_ok=True)
        
        # Inicia o servidor
        logger.info(f"Iniciando servidor em http://{args.host}:{args.port} (ambiente: {args.env})")
        app.run(host=args.host, port=args.port, debug=args.debug)
    except ImportError as e:
        logger.error(f"Erro ao importar módulos da aplicação: {e}")
        logger.error("Verifique se todas as dependências foram instaladas corretamente.")
        if args.debug:
            import traceback
            traceback.print_exc()
        return False
    except Exception as e:
        logger.error(f"Erro ao iniciar a aplicação: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return False
    
    return True

def run_diagnostic():
    """Executa apenas o diagnóstico do sistema"""
    try:
        logger.info("Iniciando diagnóstico do sistema...")
        from app.services.diagnostic_service import DiagnosticService
        
        # Cria o serviço de diagnóstico
        service = DiagnosticService()
        
        # Executa todos os diagnósticos
        logger.info("Analisando CPU...")
        cpu_result = service.analyze_cpu()
        
        logger.info("Analisando Memória...")
        memory_result = service.analyze_memory()
        
        logger.info("Analisando Disco...")
        disk_result = service.analyze_disk()
        
        logger.info("Analisando Rede...")
        network_result = service.analyze_network()
        
        logger.info("Analisando Temperatura...")
        temperature_result = service.analyze_temperature()
        
        logger.info("Analisando Segurança...")
        security_result = service.analyze_security()
        
        # Exibe um resumo dos problemas encontrados
        if service.problems:
            logger.info(f"\n{'='*20} PROBLEMAS ENCONTRADOS {'='*20}")
            for i, problem in enumerate(service.problems):
                logger.info(f"{i+1}. {problem['title']} - {problem['description']}")
                logger.info(f"   Categoria: {problem['category']}, Impacto: {problem.get('impact', 'desconhecido')}")
                if 'solution' in problem:
                    logger.info(f"   Solução: {problem['solution']}")
                logger.info("")
        else:
            logger.info("\nNenhum problema foi encontrado no seu sistema!")
        
        logger.info(f"\nPontuação de Saúde do Sistema: {service.score}/100")
        
        return True
    except Exception as e:
        logger.error(f"Erro ao executar diagnóstico: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    args = parse_arguments()
    
    # Verifica dependências antes de prosseguir
    if not verify_dependencies():
        sys.exit(1)
    
    # Configura o ambiente
    if not setup_environment(args):
        sys.exit(1)
    
    # Executa apenas o diagnóstico se solicitado
    if args.diagnostic:
        if not run_diagnostic():
            sys.exit(1)
        sys.exit(0)
    
    # Executa a aplicação
    if not run_app(args):
        sys.exit(1)
    
    logger.info("Aplicação encerrada.") 