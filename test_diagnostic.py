import os
import sys

# Configurar o modo de teste
os.environ['DIAGNOSTIC_TEST_MODE'] = '1'

# Adicionar o diretório atual ao path do Python
sys.path.append('.')

# Importar o serviço de diagnóstico
from app.services.diagnostic_service import DiagnosticService

# Criar uma instância do serviço
service = DiagnosticService()

# Executar o diagnóstico
result = service.run_diagnostics()

# Imprimir o resultado
print(f"Diagnostic score: {result.get('score')}")
print(f"CPU status: {result.get('cpu', {}).get('status')}")
print(f"Memory status: {result.get('memory', {}).get('status')}")
print(f"Disk status: {result.get('disk', {}).get('status')}")
print(f"Network status: {result.get('network', {}).get('status')}")
print("Problems:", result.get('problems'))
print("Recommendations:", result.get('recommendations')) 