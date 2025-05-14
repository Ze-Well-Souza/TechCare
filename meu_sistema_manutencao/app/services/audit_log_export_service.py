import csv
import json
import xml.etree.ElementTree as ET
import pandas as pd
from io import StringIO, BytesIO
from datetime import datetime
from app.services.audit_log_query_service import AuditLogQueryService

class AuditLogExportService:
    """
    Serviço para exportação de logs de auditoria em múltiplos formatos
    """
    
    @classmethod
    def export_logs(cls, 
                    export_format='csv', 
                    start_date=None, 
                    end_date=None, 
                    user_ids=None, 
                    actions=None, 
                    resource_types=None, 
                    ip_addresses=None):
        """
        Exportar logs de auditoria em diferentes formatos
        
        :param export_format: Formato de exportação (csv, json, xml, xlsx)
        :param start_date: Data de início para filtro
        :param end_date: Data de término para filtro
        :param user_ids: Lista de IDs de usuários
        :param actions: Lista de tipos de ações
        :param resource_types: Lista de tipos de recursos
        :param ip_addresses: Lista de endereços IP
        :return: Tupla (nome do arquivo, conteúdo do arquivo)
        """
        # Buscar logs com filtros
        logs, _ = AuditLogQueryService.advanced_search(
            start_date=start_date,
            end_date=end_date,
            user_ids=user_ids,
            actions=actions,
            resource_types=resource_types,
            ip_addresses=ip_addresses,
            page=1,
            per_page=10000  # Limite alto para exportação
        )

        # Converter logs para dicionário
        logs_data = [log.to_dict() for log in logs]

        # Gerar nome de arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"audit_logs_{timestamp}"

        # Exportar de acordo com o formato
        if export_format == 'csv':
            return cls._export_csv(logs_data, base_filename)
        elif export_format == 'json':
            return cls._export_json(logs_data, base_filename)
        elif export_format == 'xml':
            return cls._export_xml(logs_data, base_filename)
        elif export_format == 'xlsx':
            return cls._export_xlsx(logs_data, base_filename)
        else:
            raise ValueError(f"Formato de exportação não suportado: {export_format}")

    @staticmethod
    def _export_csv(logs_data, base_filename):
        """
        Exportar logs em formato CSV
        """
        output = StringIO()
        fieldnames = [
            'id', 'user_id', 'username', 'action', 
            'resource_type', 'resource_id', 'ip_address', 
            'user_agent', 'timestamp'
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for log in logs_data:
            # Remover dados complexos para CSV
            log_row = {
                'id': log['id'],
                'user_id': log['user_id'],
                'username': log['username'],
                'action': log['action'],
                'resource_type': log['resource_type'],
                'resource_id': log['resource_id'],
                'ip_address': log['ip_address'],
                'user_agent': log['user_agent'],
                'timestamp': log['timestamp']
            }
            writer.writerow(log_row)
        
        return f"{base_filename}.csv", output.getvalue()

    @staticmethod
    def _export_json(logs_data, base_filename):
        """
        Exportar logs em formato JSON
        """
        output = json.dumps(logs_data, indent=2)
        return f"{base_filename}.json", output

    @staticmethod
    def _export_xml(logs_data, base_filename):
        """
        Exportar logs em formato XML
        """
        root = ET.Element("audit_logs")
        
        for log in logs_data:
            log_elem = ET.SubElement(root, "log")
            for key, value in log.items():
                sub_elem = ET.SubElement(log_elem, key)
                sub_elem.text = str(value)
        
        output = ET.tostring(root, encoding='unicode', method='xml')
        return f"{base_filename}.xml", output

    @staticmethod
    def _export_xlsx(logs_data, base_filename):
        """
        Exportar logs em formato Excel
        """
        df = pd.DataFrame(logs_data)
        
        # Configurar buffer de saída
        output = BytesIO()
        
        # Salvar em Excel
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Audit Logs')
            
            # Ajustar largura das colunas
            worksheet = writer.sheets['Audit Logs']
            for i, col in enumerate(df.columns):
                column_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(i, i, column_len)
        
        return f"{base_filename}.xlsx", output.getvalue()

    @classmethod
    def generate_export_summary(cls, logs_data):
        """
        Gerar resumo da exportação
        
        :param logs_data: Lista de logs exportados
        :return: Dicionário com resumo da exportação
        """
        summary = {
            'total_logs': len(logs_data),
            'actions_summary': {},
            'users_summary': {},
            'resource_types_summary': {}
        }

        # Resumo por ação
        for log in logs_data:
            action = log['action']
            summary['actions_summary'][action] = summary['actions_summary'].get(action, 0) + 1

            # Resumo por usuário
            username = log['username']
            summary['users_summary'][username] = summary['users_summary'].get(username, 0) + 1

            # Resumo por tipo de recurso
            resource_type = log['resource_type']
            summary['resource_types_summary'][resource_type] = summary['resource_types_summary'].get(resource_type, 0) + 1

        return summary
