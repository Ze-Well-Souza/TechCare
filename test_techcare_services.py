#!/usr/bin/env python
"""
Script para testar as principais funcionalidades do TechCare.
Este script executa testes dos principais serviços para verificar seu funcionamento correto.
"""

from app.services.diagnostic.diagnostic_service import DiagnosticService
from app.services.cleaner_service import CleanerService
from app.services.driver_update_service import DriverUpdateService
from app.services.diagnostic.analyzers import CPUAnalyzer, MemoryAnalyzer, DiskAnalyzer
from app.services.diagnostic_service_platform import PlatformAdapter

def separador(titulo):
    """Exibe um separador formatado com o título no console"""
    linha = "=" * 80
    print(f"\n{linha}")
    print(f" {titulo} ".center(80, '='))
    print(f"{linha}\n")

def testar_diagnostico():
    """Testa o serviço de diagnóstico completo"""
    separador("TESTE DE DIAGNÓSTICO")
    
    try:
        service = DiagnosticService()
        print("✓ Serviço de diagnóstico inicializado com sucesso")
        
        print("Executando diagnóstico completo... (pode demorar alguns segundos)")
        resultado = service.run_diagnostic()
        
        print(f"✓ Diagnóstico concluído com pontuação: {resultado.get('score', 0)}")
        print(f"✓ Problemas encontrados: {len(resultado.get('issues', []))}")
        print(f"✓ Recomendações geradas: {len(resultado.get('recommendations', []))}")
        
        return True
    except Exception as e:
        print(f"✗ Erro no diagnóstico: {str(e)}")
        return False

def testar_limpeza():
    """Testa o serviço de limpeza e análise do sistema"""
    separador("TESTE DE LIMPEZA")
    
    try:
        service = CleanerService()
        print("✓ Serviço de limpeza inicializado com sucesso")
        
        print("Analisando sistema... (pode demorar alguns segundos)")
        resultado = service.analyze_system()
        
        total_cleanup = resultado.get('total_cleanup_formatted', '0 KB')
        print(f"✓ Análise concluída. Potencial de limpeza: {total_cleanup}")
        print(f"✓ Arquivos temporários: {resultado.get('temp_files', {}).get('total_files', 0)} arquivo(s)")
        
        # Verificar análise de navegadores
        browsers = list(resultado.get('browser_data', {}).keys())
        print(f"✓ Navegadores detectados: {', '.join(browsers) if browsers else 'Nenhum'}")
        
        return True
    except Exception as e:
        print(f"✗ Erro na limpeza: {str(e)}")
        return False

def testar_hardware():
    """Testa a detecção de hardware usando os analisadores oficiais"""
    separador("TESTE DE DETECÇÃO DE HARDWARE")
    
    try:
        # Usar os analisadores oficiais
        cpu_analyzer = CPUAnalyzer()
        memory_analyzer = MemoryAnalyzer()
        disk_analyzer = DiskAnalyzer()
        platform_adapter = PlatformAdapter()
        
        print("✓ Analisadores de hardware inicializados com sucesso")
        
        # Obter informações do sistema
        system_info = platform_adapter.get_system_information()
        print(f"✓ Fabricante: {system_info.get('manufacturer', 'Desconhecido')}")
        print(f"✓ Modelo: {system_info.get('model', 'Desconhecido')}")
        
        # Obter informações de CPU
        cpu_info = cpu_analyzer.analyze()
        print(f"✓ Processador: {cpu_info.get('model', 'Desconhecido')}")
        print(f"✓ Núcleos/Threads: {cpu_info.get('cores', 0)}/{cpu_info.get('threads', 0)}")
        
        # Obter informações de memória
        memory_info = memory_analyzer.analyze()
        print(f"✓ Memória total: {memory_info.get('total_gb', 0)} GB")
        print(f"✓ Memória em uso: {memory_info.get('percent_used', 0)}%")
        
        # Obter informações de disco
        disk_info = disk_analyzer.analyze()
        drives = disk_info.get('drives', [])
        print(f"✓ Discos lógicos detectados: {len(drives)}")
        
        return True
    except Exception as e:
        print(f"✗ Erro na detecção de hardware: {str(e)}")
        return False

def testar_drivers():
    """Testa o serviço de atualização de drivers"""
    separador("TESTE DE ATUALIZAÇÃO DE DRIVERS")
    
    try:
        service = DriverUpdateService()
        print("✓ Serviço de drivers inicializado com sucesso")
        
        print("Escaneando drivers... (pode demorar alguns segundos)")
        scan_result = service.scan_drivers()
        
        total = scan_result.get('total_count', 0)
        updated = scan_result.get('updated_count', 0)
        outdated = scan_result.get('outdated_count', 0)
        issues = scan_result.get('issue_count', 0)
        
        print(f"✓ Total de drivers: {total}")
        print(f"✓ Drivers atualizados: {updated}")
        print(f"✓ Drivers desatualizados: {outdated}")
        print(f"✓ Drivers com problemas: {issues}")
        
        return True
    except Exception as e:
        print(f"✗ Erro na verificação de drivers: {str(e)}")
        return False

def main():
    """Função principal que executa todos os testes"""
    print("🔍 Iniciando verificação completa do TechCare")
    
    # Lista para armazenar o status de cada teste
    status = []
    
    # Testar diagnóstico
    status.append(testar_diagnostico())
    
    # Testar limpeza
    status.append(testar_limpeza())
    
    # Testar detecção de hardware
    status.append(testar_hardware())
    
    # Testar drivers
    status.append(testar_drivers())
    
    # Resumo final
    separador("RESUMO DOS TESTES")
    
    total = len(status)
    passed = sum(status)
    
    print(f"Total de testes: {total}")
    print(f"Testes bem-sucedidos: {passed}")
    print(f"Testes com erro: {total - passed}")
    
    if passed == total:
        print("\n✅ TODAS AS FUNCIONALIDADES ESTÃO OPERANDO CORRETAMENTE! ✅")
    else:
        print("\n⚠️ ALGUMAS FUNCIONALIDADES APRESENTARAM PROBLEMAS! ⚠️")
        print("Por favor, verifique as mensagens de erro acima.")

if __name__ == "__main__":
    main() 