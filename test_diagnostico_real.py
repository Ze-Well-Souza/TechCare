import sys
import os
import logging
import json
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DiagnosticoTest")

# Adicionar o diretório raiz ao sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from app.services.diagnostic.diagnostic_service import DiagnosticService
    logger.info("Usando versão refatorada do DiagnosticService")
    versao_refatorada = True
except ImportError:
    try:
        from app.services.diagnostic_service import DiagnosticService
        logger.info("Usando versão original do DiagnosticService")
        versao_refatorada = False
    except ImportError:
        logger.error("Não foi possível importar o DiagnosticService")
        sys.exit(1)

def main():
    """Teste real do serviço de diagnóstico"""
    logger.info("Iniciando teste do serviço de diagnóstico...")
    
    # Criar instância do serviço
    try:
        service = DiagnosticService()
        logger.info("Serviço instanciado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao instanciar serviço: {str(e)}")
        sys.exit(1)
    
    # Executar análise completa
    try:
        if versao_refatorada:
            # Usando a API refatorada
            logger.info("Iniciando diagnóstico completo...")
            resultado = service.run_diagnostic()
            logger.info(f"Diagnóstico completo concluído com score: {resultado.get('health_score', 'N/A')}")
            
            # Verificar problemas
            problemas = resultado.get('problems', [])
            logger.info(f"Total de problemas encontrados: {len(problemas)}")
            
            # Verificar recomendações
            recomendacoes = resultado.get('recommendations', [])
            logger.info(f"Total de recomendações geradas: {len(recomendacoes)}")
            
            # Verificar componentes analisados
            componentes = resultado.get('components', {})
            logger.info(f"Componentes analisados: {', '.join(componentes.keys())}")
            
        else:
            # Usando a API original
            logger.info("Iniciando análise de CPU...")
            cpu_result = service.analyze_cpu()
            logger.info(f"Análise de CPU concluída com score: {service.score}")
            
            logger.info("Iniciando análise de memória...")
            memory_result = service.analyze_memory()
            logger.info(f"Análise de memória concluída com score: {service.score}")
            
            logger.info("Iniciando análise de disco...")
            disk_result = service.analyze_disk()
            logger.info(f"Análise de disco concluída com score: {service.score}")
            
            logger.info("Iniciando análise de rede...")
            network_result = service.analyze_network()
            logger.info(f"Análise de rede concluída com score: {service.score}")
            
            logger.info("Iniciando análise de inicialização...")
            startup_result = service.analyze_startup()
            logger.info(f"Análise de inicialização concluída com score: {service.score}")
            
            logger.info("Iniciando análise de segurança...")
            security_result = service.analyze_security()
            logger.info(f"Análise de segurança concluída com score: {service.score}")
            
            # Verificar geração de recomendações
            logger.info("Gerando recomendações...")
            recommendations = service.generate_recommendations()
            logger.info(f"Geradas {len(recommendations)} recomendações")
            
            # Converter para o formato unificado para salvar
            resultado = {
                "score": service.score,
                "problems": service.problems,
                "cpu": service.results.get("cpu", {}),
                "memory": service.results.get("memory", {}),
                "disk": service.results.get("disk", {}),
                "network": service.results.get("network", {}),
                "startup": service.results.get("startup", {}),
                "security": service.results.get("security", {}),
                "recommendations": recommendations
            }
            problemas = service.problems
            
        # Salvar resultado completo para análise
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = "resultados_testes"
        os.makedirs(results_dir, exist_ok=True)
        
        results_file = os.path.join(results_dir, f"diagnostic_test_{timestamp}.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=4, default=str)
        
        logger.info(f"Resultados salvos em {results_file}")
        
        # Mostrar problemas encontrados
        for i, problem in enumerate(problemas, 1):
            categoria = problem.get('category', 'desconhecida')
            titulo = problem.get('title', problem.get('description', 'Problema sem título'))
            logger.info(f"Problema {i}: {categoria} - {titulo}")
        
        logger.info("Teste concluído com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"Erro durante a análise: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 