"""
Gerador de Recomendações para o Diagnóstico
==========================================

Este módulo é responsável por gerar recomendações baseadas nos problemas
encontrados durante o diagnóstico do sistema.
"""

import logging
from typing import Dict, Any, List, Optional
import re

logger = logging.getLogger(__name__)

class RecommendationGenerator:
    """
    Gera recomendações personalizadas com base nos problemas encontrados.
    """
    
    def __init__(self):
        """Inicializa o gerador de recomendações"""
        self.recommendation_templates = {
            # Templates para CPU
            'cpu_high_usage': "Reduza o número de aplicativos em execução para diminuir o uso da CPU.",
            'cpu_overheating': "Verifique o sistema de refrigeração do computador e limpe a poeira acumulada.",
            'cpu_throttling': "Seu processador está reduzindo a velocidade para evitar superaquecimento. Verifique a refrigeração.",
            
            # Templates para Memória
            'memory_high_usage': "Feche aplicativos não utilizados para liberar memória RAM.",
            'memory_leak': "Identifique e reinicie aplicativos com vazamento de memória.",
            'memory_upgrade': "Considere atualizar a memória RAM do sistema para melhor desempenho.",
            
            # Templates para Disco
            'disk_space_low': "Libere espaço em disco excluindo arquivos desnecessários ou utilizando a ferramenta de limpeza de disco.",
            'disk_fragmentation': "Execute a desfragmentação de disco para melhorar o desempenho.",
            'disk_health_warning': "Faça backup dos seus dados importantes, o disco pode estar apresentando sinais de falha.",
            'disk_slow': "Considere atualizar para um SSD para melhorar drasticamente o desempenho do sistema.",
            
            # Templates para Rede
            'network_slow': "Verifique sua conexão com a internet ou tente conectar-se mais próximo do roteador.",
            'network_driver_outdated': "Atualize os drivers da placa de rede para melhorar a estabilidade da conexão.",
            'network_interface_error': "Reinicie o adaptador de rede ou verifique se há problemas físicos na conexão.",
            
            # Templates para Iniciação
            'startup_too_many_items': "Reduza o número de programas que iniciam com o Windows para melhorar o tempo de inicialização.",
            'startup_service_delay': "Otimize os serviços em execução para melhorar o desempenho de inicialização.",
            
            # Templates para Segurança
            'security_antivirus_disabled': "Ative seu software antivírus para proteger seu sistema.",
            'security_firewall_disabled': "Ative o firewall para proteger seu sistema contra ameaças externas.",
            'security_updates_missing': "Mantenha seu sistema atualizado para proteger contra vulnerabilidades de segurança.",
            
            # Templates para Drivers
            'driver_outdated': "Atualize os drivers desatualizados para melhorar a estabilidade e desempenho.",
            'driver_missing': "Instale os drivers ausentes para garantir que todos os dispositivos funcionem corretamente."
        }
        
        # Defições de categoria-problema-solução para casos complexos
        self.issue_handlers = {
            'cpu': self._handle_cpu_issues,
            'memory': self._handle_memory_issues,
            'disk': self._handle_disk_issues,
            'network': self._handle_network_issues,
            'startup': self._handle_startup_issues,
            'security': self._handle_security_issues,
            'driver': self._handle_driver_issues
        }
    
    def generate(self, issues: List[Dict[str, Any]]) -> List[str]:
        """
        Gera recomendações baseadas nos problemas encontrados.
        
        Args:
            issues: Lista de problemas encontrados durante o diagnóstico
            
        Returns:
            List[str]: Lista de recomendações
        """
        if not issues:
            return ["Nenhum problema significativo foi encontrado no sistema."]
        
        try:
            # Agrupa problemas por categoria
            categorized_issues = self._categorize_issues(issues)
            
            # Gera recomendações para cada categoria
            recommendations = []
            for category, category_issues in categorized_issues.items():
                # Verifica se existe um handler específico para esta categoria
                if category in self.issue_handlers:
                    category_recommendations = self.issue_handlers[category](category_issues)
                    recommendations.extend(category_recommendations)
                else:
                    # Processamento genérico para categorias sem handler específico
                    for issue in category_issues:
                        if 'recommendation' in issue:
                            recommendations.append(issue['recommendation'])
            
            # Adiciona recomendação genérica se não houver nenhuma específica
            if not recommendations:
                for issue in issues:
                    if 'description' in issue:
                        recommendations.append(f"Corrija o problema: {issue['description']}")
            
            # Remove duplicatas e ordena por gravidade
            unique_recommendations = self._prioritize_and_deduplicate(recommendations, issues)
            
            return unique_recommendations
            
        except Exception as e:
            logger.error(f"Erro ao gerar recomendações: {str(e)}", exc_info=True)
            # Fallback para recomendações diretas das issues
            fallback_recommendations = []
            for issue in issues:
                if 'recommendation' in issue:
                    fallback_recommendations.append(issue['recommendation'])
            
            return list(set(fallback_recommendations)) if fallback_recommendations else ["Verifique os problemas identificados no diagnóstico."]
    
    def _categorize_issues(self, issues: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Agrupa problemas por categoria.
        
        Args:
            issues: Lista de problemas
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Problemas agrupados por categoria
        """
        categorized = {}
        
        for issue in issues:
            # Tenta determinar a categoria do problema
            category = None
            
            # Verifica se o problema tem uma categoria explícita
            if 'category' in issue:
                category = issue['category']
            else:
                # Tenta inferir a categoria a partir da descrição ou outros campos
                description = issue.get('description', '')
                
                if any(keyword in description.lower() for keyword in ['cpu', 'processador', 'núcleo']):
                    category = 'cpu'
                elif any(keyword in description.lower() for keyword in ['memória', 'ram', 'memory']):
                    category = 'memory'
                elif any(keyword in description.lower() for keyword in ['disco', 'disk', 'hdd', 'ssd', 'armazenamento']):
                    category = 'disk'
                elif any(keyword in description.lower() for keyword in ['rede', 'network', 'wifi', 'internet', 'conexão', 'ethernet']):
                    category = 'network'
                elif any(keyword in description.lower() for keyword in ['inicialização', 'startup', 'boot', 'iniciar']):
                    category = 'startup'
                elif any(keyword in description.lower() for keyword in ['segurança', 'security', 'antivírus', 'firewall', 'vírus']):
                    category = 'security'
                elif any(keyword in description.lower() for keyword in ['driver', 'dispositivo', 'device']):
                    category = 'driver'
                else:
                    category = 'general'
            
            # Adiciona o problema à categoria
            if category not in categorized:
                categorized[category] = []
            
            categorized[category].append(issue)
        
        return categorized
    
    def _prioritize_and_deduplicate(self, recommendations: List[str], issues: List[Dict[str, Any]]) -> List[str]:
        """
        Remove recomendações duplicadas e prioriza por gravidade.
        
        Args:
            recommendations: Lista de recomendações
            issues: Lista de problemas (para determinar gravidade)
            
        Returns:
            List[str]: Lista de recomendações únicas e priorizadas
        """
        # Remove duplicatas exatas
        unique_recommendations = list(set(recommendations))
        
        # Detecta e combina recomendações similares
        i = 0
        while i < len(unique_recommendations):
            j = i + 1
            while j < len(unique_recommendations):
                # Verifica similaridade usando coeficiente de Jaccard simplificado
                if self._are_similar(unique_recommendations[i], unique_recommendations[j]):
                    # Combina as recomendações
                    unique_recommendations[i] = self._combine_recommendations(
                        unique_recommendations[i], 
                        unique_recommendations[j]
                    )
                    unique_recommendations.pop(j)
                else:
                    j += 1
            i += 1
        
        # Mapeia gravidade dos problemas para as recomendações
        severity_map = {
            'high': 3,
            'medium': 2,
            'low': 1
        }
        
        recommendation_severity = {}
        for issue in issues:
            if 'recommendation' in issue and 'severity' in issue:
                severity = issue.get('severity', 'low')
                severity_value = severity_map.get(severity, 1)
                
                for rec in unique_recommendations:
                    if issue['recommendation'] in rec or rec in issue['recommendation']:
                        if rec in recommendation_severity:
                            recommendation_severity[rec] = max(recommendation_severity[rec], severity_value)
                        else:
                            recommendation_severity[rec] = severity_value
        
        # Ordena por gravidade (alta para baixa)
        sorted_recommendations = sorted(
            unique_recommendations,
            key=lambda r: recommendation_severity.get(r, 0),
            reverse=True
        )
        
        return sorted_recommendations
    
    def _are_similar(self, text1: str, text2: str) -> bool:
        """
        Verifica se dois textos são similares.
        
        Args:
            text1: Primeiro texto
            text2: Segundo texto
            
        Returns:
            bool: True se os textos forem similares
        """
        # Simplifica os textos
        t1 = re.sub(r'[^\w\s]', '', text1.lower())
        t2 = re.sub(r'[^\w\s]', '', text2.lower())
        
        # Conjuntos de palavras
        words1 = set(t1.split())
        words2 = set(t2.split())
        
        # Coeficiente de Jaccard
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        similarity = intersection / union if union > 0 else 0
        
        # Considera similar se compartilhar mais de 50% das palavras
        return similarity > 0.5
    
    def _combine_recommendations(self, rec1: str, rec2: str) -> str:
        """
        Combina duas recomendações similares.
        
        Args:
            rec1: Primeira recomendação
            rec2: Segunda recomendação
            
        Returns:
            str: Recomendação combinada
        """
        # Usa a recomendação mais longa como base
        if len(rec1) >= len(rec2):
            return rec1
        else:
            return rec2
    
    def _handle_cpu_issues(self, issues: List[Dict[str, Any]]) -> List[str]:
        """
        Processa problemas específicos de CPU.
        
        Args:
            issues: Lista de problemas de CPU
            
        Returns:
            List[str]: Recomendações para os problemas de CPU
        """
        recommendations = []
        
        usage_issues = [i for i in issues if 'high usage' in i.get('description', '').lower()]
        temp_issues = [i for i in issues if 'temperatura' in i.get('description', '').lower() or 'temp' in i.get('description', '').lower()]
        perf_issues = [i for i in issues if 'desempenho' in i.get('description', '').lower() or 'performance' in i.get('description', '').lower()]
        
        if usage_issues:
            recommendations.append(self.recommendation_templates['cpu_high_usage'])
            
        if temp_issues:
            recommendations.append(self.recommendation_templates['cpu_overheating'])
            
        if perf_issues:
            recommendations.append("Execute a verificação de desempenho da CPU e compare com benchmarks de referência.")
        
        # Adiciona recomendações diretas das issues
        for issue in issues:
            if 'recommendation' in issue:
                recommendations.append(issue['recommendation'])
        
        return list(set(recommendations))
    
    def _handle_memory_issues(self, issues: List[Dict[str, Any]]) -> List[str]:
        """
        Processa problemas específicos de memória.
        
        Args:
            issues: Lista de problemas de memória
            
        Returns:
            List[str]: Recomendações para os problemas de memória
        """
        recommendations = []
        
        usage_issues = [i for i in issues if 'high usage' in i.get('description', '').lower() or 'uso elevado' in i.get('description', '').lower()]
        capacity_issues = [i for i in issues if 'capacity' in i.get('description', '').lower() or 'capacidade' in i.get('description', '').lower()]
        
        if usage_issues:
            recommendations.append(self.recommendation_templates['memory_high_usage'])
            
        if capacity_issues:
            recommendations.append(self.recommendation_templates['memory_upgrade'])
        
        # Verifica se há vazamentos de memória
        leak_terms = ['leak', 'vazamento', 'crescente', 'increasing']
        if any(any(term in i.get('description', '').lower() for term in leak_terms) for i in issues):
            recommendations.append(self.recommendation_templates['memory_leak'])
        
        # Adiciona recomendações diretas das issues
        for issue in issues:
            if 'recommendation' in issue:
                recommendations.append(issue['recommendation'])
        
        return list(set(recommendations))
    
    def _handle_disk_issues(self, issues: List[Dict[str, Any]]) -> List[str]:
        """
        Processa problemas específicos de disco.
        
        Args:
            issues: Lista de problemas de disco
            
        Returns:
            List[str]: Recomendações para os problemas de disco
        """
        recommendations = []
        
        space_issues = [i for i in issues if 'space' in i.get('description', '').lower() or 'espaço' in i.get('description', '').lower()]
        health_issues = [i for i in issues if 'health' in i.get('description', '').lower() or 'saúde' in i.get('description', '').lower() or 'erro' in i.get('description', '').lower()]
        performance_issues = [i for i in issues if 'performance' in i.get('description', '').lower() or 'desempenho' in i.get('description', '').lower() or 'lento' in i.get('description', '').lower()]
        
        if space_issues:
            recommendations.append(self.recommendation_templates['disk_space_low'])
            
        if health_issues:
            recommendations.append(self.recommendation_templates['disk_health_warning'])
            
        if performance_issues:
            # Verifica se é um HDD
            if any('hdd' in i.get('description', '').lower() for i in issues):
                recommendations.append(self.recommendation_templates['disk_slow'])
            
            # Verifica fragmentação
            if any('fragment' in i.get('description', '').lower() for i in issues):
                recommendations.append(self.recommendation_templates['disk_fragmentation'])
        
        # Adiciona recomendações diretas das issues
        for issue in issues:
            if 'recommendation' in issue:
                recommendations.append(issue['recommendation'])
        
        return list(set(recommendations))
    
    def _handle_network_issues(self, issues: List[Dict[str, Any]]) -> List[str]:
        """
        Processa problemas específicos de rede.
        
        Args:
            issues: Lista de problemas de rede
            
        Returns:
            List[str]: Recomendações para os problemas de rede
        """
        recommendations = []
        
        speed_issues = [i for i in issues if 'speed' in i.get('description', '').lower() or 'velocidade' in i.get('description', '').lower() or 'lenta' in i.get('description', '').lower()]
        driver_issues = [i for i in issues if 'driver' in i.get('description', '').lower()]
        connection_issues = [i for i in issues if 'connection' in i.get('description', '').lower() or 'conexão' in i.get('description', '').lower() or 'conexao' in i.get('description', '').lower()]
        
        if speed_issues:
            recommendations.append(self.recommendation_templates['network_slow'])
            
        if driver_issues:
            recommendations.append(self.recommendation_templates['network_driver_outdated'])
            
        if connection_issues:
            recommendations.append(self.recommendation_templates['network_interface_error'])
        
        # Adiciona recomendações diretas das issues
        for issue in issues:
            if 'recommendation' in issue:
                recommendations.append(issue['recommendation'])
        
        return list(set(recommendations))
    
    def _handle_startup_issues(self, issues: List[Dict[str, Any]]) -> List[str]:
        """
        Processa problemas específicos de inicialização.
        
        Args:
            issues: Lista de problemas de inicialização
            
        Returns:
            List[str]: Recomendações para os problemas de inicialização
        """
        recommendations = []
        
        too_many_issues = [i for i in issues if 'many' in i.get('description', '').lower() or 'muitos' in i.get('description', '').lower()]
        service_issues = [i for i in issues if 'service' in i.get('description', '').lower() or 'serviço' in i.get('description', '').lower()]
        
        if too_many_issues:
            recommendations.append(self.recommendation_templates['startup_too_many_items'])
            
        if service_issues:
            recommendations.append(self.recommendation_templates['startup_service_delay'])
        
        # Adiciona recomendações diretas das issues
        for issue in issues:
            if 'recommendation' in issue:
                recommendations.append(issue['recommendation'])
        
        return list(set(recommendations))
    
    def _handle_security_issues(self, issues: List[Dict[str, Any]]) -> List[str]:
        """
        Processa problemas específicos de segurança.
        
        Args:
            issues: Lista de problemas de segurança
            
        Returns:
            List[str]: Recomendações para os problemas de segurança
        """
        recommendations = []
        
        antivirus_issues = [i for i in issues if 'antivirus' in i.get('description', '').lower() or 'antivírus' in i.get('description', '').lower()]
        firewall_issues = [i for i in issues if 'firewall' in i.get('description', '').lower()]
        update_issues = [i for i in issues if 'update' in i.get('description', '').lower() or 'atualização' in i.get('description', '').lower()]
        
        if antivirus_issues:
            recommendations.append(self.recommendation_templates['security_antivirus_disabled'])
            
        if firewall_issues:
            recommendations.append(self.recommendation_templates['security_firewall_disabled'])
            
        if update_issues:
            recommendations.append(self.recommendation_templates['security_updates_missing'])
        
        # Adiciona recomendações diretas das issues
        for issue in issues:
            if 'recommendation' in issue:
                recommendations.append(issue['recommendation'])
        
        return list(set(recommendations))
    
    def _handle_driver_issues(self, issues: List[Dict[str, Any]]) -> List[str]:
        """
        Processa problemas específicos de drivers.
        
        Args:
            issues: Lista de problemas de drivers
            
        Returns:
            List[str]: Recomendações para os problemas de drivers
        """
        recommendations = []
        
        outdated_issues = [i for i in issues if 'outdated' in i.get('description', '').lower() or 'desatualizado' in i.get('description', '').lower()]
        missing_issues = [i for i in issues if 'missing' in i.get('description', '').lower() or 'ausente' in i.get('description', '').lower()]
        
        if outdated_issues:
            recommendations.append(self.recommendation_templates['driver_outdated'])
            
        if missing_issues:
            recommendations.append(self.recommendation_templates['driver_missing'])
        
        # Adiciona recomendações diretas das issues
        for issue in issues:
            if 'recommendation' in issue:
                recommendations.append(issue['recommendation'])
        
        return list(set(recommendations)) 