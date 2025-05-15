#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para execução completa da suíte de testes do TechCare
Gera relatórios detalhados de cobertura e identifica áreas que precisam de melhorias
"""

import os
import sys
import subprocess
import datetime
import json
import re
from pathlib import Path

# Configurações
OUTPUT_DIR = Path("tests/reports")
COVERAGE_HTML_DIR = Path("tests/coverage_html")
COVERAGE_THRESHOLD = 75  # Meta de cobertura
CRITICAL_MODULES = [
    "app/services/diagnostic_service.py",
    "app/services/cleaner_service.py",
    "app/services/driver_update_service.py",
    "app/services/repair_service.py"
]

def setup_environment():
    """Prepara o ambiente para execução dos testes"""
    print("🔧 Configurando ambiente de testes...")
    
    # Garantir que a variável de ambiente para testes está definida
    os.environ["FLASK_ENV"] = "testing"
    os.environ["DIAGNOSTIC_TEST_MODE"] = "1"
    
    # Criar diretórios de saída se não existirem
    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
    COVERAGE_HTML_DIR.mkdir(exist_ok=True, parents=True)
    
    print("✅ Ambiente configurado com sucesso\n")

def run_linting():
    """Executa verificação de estilo de código"""
    print("🔍 Executando linting do código...")
    
    try:
        result = subprocess.run(
            ["flake8", "app", "tests", "--count", "--select=E9,F63,F7,F82", "--show-source", "--statistics"],
            capture_output=True,
            text=True,
            check=False
        )
        
        lint_output = result.stdout + result.stderr
        lint_report_path = OUTPUT_DIR / "lint_report.txt"
        
        with open(lint_report_path, "w", encoding="utf-8") as f:
            f.write(lint_output)
        
        error_count = 0
        if result.returncode != 0:
            # Contar erros
            match = re.search(r"(\d+)\s+error", lint_output)
            if match:
                error_count = int(match.group(1))
            
            print(f"⚠️ Foram encontrados {error_count} problemas de linting")
            print(f"📄 Relatório completo salvo em {lint_report_path}")
        else:
            print("✅ Nenhum problema de linting encontrado")
        
        return error_count
    except Exception as e:
        print(f"❌ Erro ao executar linting: {str(e)}")
        return -1

def run_tests():
    """Executa todos os testes e gera relatório de cobertura"""
    print("\n🧪 Executando testes com cobertura...")
    
    start_time = datetime.datetime.now()
    
    try:
        result = subprocess.run(
            [
                "pytest", 
                "-xvs", 
                "--cov=app", 
                "--cov-report=term-missing",
                f"--cov-report=html:{COVERAGE_HTML_DIR}",
                f"--cov-report=json:{OUTPUT_DIR / 'coverage.json'}"
            ],
            capture_output=True,
            text=True,
            check=False
        )
        
        test_output = result.stdout + result.stderr
        test_report_path = OUTPUT_DIR / "test_report.txt"
        
        with open(test_report_path, "w", encoding="utf-8") as f:
            f.write(test_output)
        
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Extrair estatísticas de testes
        tests_total = 0
        tests_passed = 0
        
        total_match = re.search(r"collected\s+(\d+)\s+item", test_output)
        if total_match:
            tests_total = int(total_match.group(1))
        
        if result.returncode == 0:
            tests_passed = tests_total
        else:
            # Se houve falhas, tentar extrair quantos passaram
            passed_match = re.search(r"(\d+) passed", test_output)
            if passed_match:
                tests_passed = int(passed_match.group(1))
        
        print(f"📊 Testes concluídos em {duration:.2f} segundos")
        print(f"📊 Total de testes: {tests_total}, Passaram: {tests_passed}")
        print(f"📄 Relatório completo salvo em {test_report_path}")
        
        return tests_total, tests_passed, test_output, result.returncode == 0
    except Exception as e:
        print(f"❌ Erro ao executar testes: {str(e)}")
        return 0, 0, str(e), False

def analyze_coverage():
    """Analisa o relatório de cobertura e identifica áreas críticas"""
    print("\n📈 Analisando cobertura de código...")
    
    try:
        coverage_json_path = OUTPUT_DIR / "coverage.json"
        if not coverage_json_path.exists():
            print(f"❌ Arquivo de cobertura não encontrado: {coverage_json_path}")
            return None
        
        with open(coverage_json_path, "r", encoding="utf-8") as f:
            coverage_data = json.load(f)
        
        # Calcular cobertura total
        total_statements = 0
        total_covered = 0
        modules_coverage = []
        
        for file_path, data in coverage_data["files"].items():
            statements = data["summary"]["num_statements"]
            covered = data["summary"]["covered_statements"]
            total_statements += statements
            total_covered += covered
            
            if statements > 0:
                coverage_pct = (covered / statements) * 100
                modules_coverage.append({
                    "file": file_path,
                    "statements": statements,
                    "covered": covered,
                    "coverage": coverage_pct,
                    "is_critical": file_path in CRITICAL_MODULES
                })
        
        overall_coverage = (total_covered / total_statements * 100) if total_statements > 0 else 0
        
        # Ordenar módulos por cobertura (ascendente)
        modules_coverage.sort(key=lambda x: x["coverage"])
        
        # Identificar módulos com baixa cobertura
        low_coverage_modules = [m for m in modules_coverage if m["coverage"] < COVERAGE_THRESHOLD]
        
        # Identificar módulos críticos com baixa cobertura
        critical_low_coverage = [m for m in low_coverage_modules if m["is_critical"]]
        
        print(f"📊 Cobertura geral: {overall_coverage:.1f}%")
        print(f"📊 Meta de cobertura: {COVERAGE_THRESHOLD}%")
        
        if overall_coverage < COVERAGE_THRESHOLD:
            print(f"⚠️ Cobertura abaixo da meta ({COVERAGE_THRESHOLD}%)")
        else:
            print(f"✅ Cobertura acima da meta ({COVERAGE_THRESHOLD}%)")
        
        print(f"\n⚠️ Módulos com cobertura abaixo da meta: {len(low_coverage_modules)}")
        for module in low_coverage_modules[:5]:  # Mostrar apenas os 5 piores
            print(f"   - {module['file']}: {module['coverage']:.1f}% ({module['covered']}/{module['statements']})")
        
        if critical_low_coverage:
            print(f"\n❌ Módulos CRÍTICOS com cobertura abaixo da meta: {len(critical_low_coverage)}")
            for module in critical_low_coverage:
                print(f"   - {module['file']}: {module['coverage']:.1f}% ({module['covered']}/{module['statements']})")
        
        # Gerar recomendações
        recommendations = []
        
        if critical_low_coverage:
            recommendations.append(f"Priorize testes para módulos críticos: {', '.join([m['file'] for m in critical_low_coverage])}")
        
        if overall_coverage < COVERAGE_THRESHOLD:
            gap = COVERAGE_THRESHOLD - overall_coverage
            statements_needed = int((total_statements * COVERAGE_THRESHOLD / 100) - total_covered)
            recommendations.append(f"Para atingir {COVERAGE_THRESHOLD}% de cobertura, é necessário cobrir aproximadamente mais {statements_needed} statements (aumento de {gap:.1f}%)")
        
        print("\n🔍 Recomendações:")
        for rec in recommendations:
            print(f"   - {rec}")
        
        return {
            "overall_coverage": overall_coverage,
            "total_statements": total_statements,
            "covered_statements": total_covered,
            "low_coverage_modules": low_coverage_modules,
            "critical_low_coverage": critical_low_coverage,
            "recommendations": recommendations
        }
    except Exception as e:
        print(f"❌ Erro ao analisar cobertura: {str(e)}")
        return None

def generate_summary_report(lint_count, tests_data, coverage_data):
    """Gera um relatório resumido com todas as informações"""
    tests_total, tests_passed, _, tests_success = tests_data
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    summary = {
        "timestamp": timestamp,
        "lint": {
            "error_count": lint_count,
            "status": "success" if lint_count == 0 else "failure"
        },
        "tests": {
            "total": tests_total,
            "passed": tests_passed,
            "failed": tests_total - tests_passed,
            "status": "success" if tests_success else "failure"
        },
        "coverage": coverage_data
    }
    
    # Salvar relatório como JSON
    summary_path = OUTPUT_DIR / "summary_report.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    
    # Também gerar um markdown para fácil visualização
    markdown_path = OUTPUT_DIR / "summary_report.md"
    
    with open(markdown_path, "w", encoding="utf-8") as f:
        f.write(f"# Relatório de Qualidade de Código - TechCare\n\n")
        f.write(f"**Data/Hora:** {timestamp}\n\n")
        
        f.write("## Resumo\n\n")
        
        # Status geral
        overall_status = "✅ APROVADO" if lint_count == 0 and tests_success and coverage_data["overall_coverage"] >= COVERAGE_THRESHOLD else "❌ REPROVADO"
        f.write(f"**Status Geral:** {overall_status}\n\n")
        
        # Linting
        lint_status = "✅ Aprovado" if lint_count == 0 else f"❌ Reprovado ({lint_count} erros)"
        f.write(f"**Linting:** {lint_status}\n\n")
        
        # Testes
        test_status = "✅ Aprovado" if tests_success else f"❌ Reprovado ({tests_total - tests_passed} falhas)"
        f.write(f"**Testes:** {test_status} ({tests_passed}/{tests_total} passaram)\n\n")
        
        # Cobertura
        coverage_status = "✅ Aprovado" if coverage_data["overall_coverage"] >= COVERAGE_THRESHOLD else "❌ Reprovado"
        f.write(f"**Cobertura:** {coverage_status} ({coverage_data['overall_coverage']:.1f}% / meta: {COVERAGE_THRESHOLD}%)\n\n")
        
        # Recomendações
        f.write("## Recomendações\n\n")
        for rec in coverage_data.get("recommendations", []):
            f.write(f"- {rec}\n")
        
        # Módulos críticos com baixa cobertura
        if coverage_data.get("critical_low_coverage"):
            f.write("\n## Módulos Críticos com Baixa Cobertura\n\n")
            for module in coverage_data["critical_low_coverage"]:
                f.write(f"- **{module['file']}**: {module['coverage']:.1f}% ({module['covered']}/{module['statements']})\n")
    
    print(f"\n📄 Relatório resumido salvo em {markdown_path}")
    return summary

def main():
    """Função principal para execução da suite completa de testes"""
    print("\n🚀 Iniciando execução da suite completa de testes do TechCare")
    print("=" * 80)
    
    # Configurar ambiente
    setup_environment()
    
    try:
        # Executar testes sem cobertura
        print("\n🧪 Executando testes...")
        result = subprocess.run(
            ["pytest", "-xvs"],
            check=False
        )
        
        if result.returncode == 0:
            print("\n✅ Todos os testes passaram com sucesso!")
        else:
            print(f"\n❌ Alguns testes falharam (código de saída: {result.returncode})")
        
        return result.returncode
    except Exception as e:
        print(f"\n❌ Erro ao executar testes: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 