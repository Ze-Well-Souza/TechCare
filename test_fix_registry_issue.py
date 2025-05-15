import sys
import os
import json
import platform

from app.services.cleaner_service import CleanerService

# Configuração básica
print(f"Sistema: {platform.system()}")
print(f"Versão Python: {sys.version}")

# Criar instância do serviço
cleaner = CleanerService()
print(f"Service iniciado, is_windows: {cleaner.is_windows}")

# Verificar se estamos no Windows
if not cleaner.is_windows:
    print("Este teste só funciona no Windows")
    sys.exit(0)

# Criar um problema de teste simulado para correção
test_issue = {
    "key": "HKEY_CURRENT_USER",
    "path": "Software\\TechCare\\Test",
    "name": "TestValue",
    "issue_type": "invalid_value",
    "description": "Valor de teste para validação",
    "action": "delete"
}

print("Resultados da análise do registro:")
registry_issues = cleaner._analyze_registry()
print(json.dumps(registry_issues, indent=2))

print("\nTestando método _fix_registry_issue com problema simulado:")
try:
    # Tentar corrigir o problema
    result = cleaner._fix_registry_issue(test_issue)
    print(f"Resultado: {result}")
except Exception as e:
    print(f"Erro: {e}")
    print(f"Tipo: {type(e)}")
    import traceback
    traceback.print_exc()

print("\nTestando clean_registry:")
try:
    # Tentar limpar o registro
    result = cleaner.clean_registry()
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"Erro: {e}")
    print(f"Tipo: {type(e)}")
    import traceback
    traceback.print_exc()

print("\nTeste concluído") 