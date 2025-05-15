"""
Repositório para armazenamento e recuperação de diagnósticos.
"""
import datetime
import uuid
from typing import Dict, List, Optional, Any
import json
import os
from pathlib import Path
from collections import defaultdict
import logging
import gc

logger = logging.getLogger(__name__)

class DiagnosticRepository:
    """
    Repositório para armazenamento e recuperação de diagnósticos.
    Implementa armazenamento em memória com persistência opcional em arquivos.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Inicializa o repositório de diagnósticos
        
        Args:
            storage_path: Caminho para armazenamento em disco (opcional)
        """
        # Inicializa _diagnostics como defaultdict para evitar KeyError
        self._diagnostics = defaultdict(list)
        self.storage_path = storage_path
        
        if storage_path:
            self.storage_dir = Path(storage_path)
            if not self.storage_dir.exists():
                self.storage_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"Diretório de armazenamento criado: {self.storage_dir}")
    
    def save(self, diagnostic_data: Dict[str, Any]) -> str:
        """
        Salva um diagnóstico
        
        Args:
            diagnostic_data: Dados do diagnóstico
            
        Returns:
            ID do diagnóstico salvo
        """
        # Gera ID se não existir
        if 'id' not in diagnostic_data:
            diagnostic_data['id'] = f"diag-{uuid.uuid4().hex[:8]}"
        
        # Adiciona timestamp se não existir
        if 'timestamp' not in diagnostic_data:
            diagnostic_data['timestamp'] = datetime.datetime.utcnow().isoformat()
        
        # Identifica o usuário
        user_id = diagnostic_data.get('user_id', 'anonymous')
        
        # Como estamos usando defaultdict, podemos simplesmente adicionar ao valor
        # O defaultdict criará uma lista vazia para uma chave inexistente
        self._diagnostics[user_id].append(diagnostic_data)
        
        # Persiste em disco se configurado
        if self.storage_path:
            self._save_to_disk(diagnostic_data)
        
        logger.info(f"Diagnóstico {diagnostic_data['id']} salvo para usuário {user_id}")
        return diagnostic_data['id']
    
    def _save_to_disk(self, diagnostic_data: Dict[str, Any]) -> None:
        """
        Salva um diagnóstico em disco
        
        Args:
            diagnostic_data: Dados do diagnóstico
        """
        try:
            user_id = diagnostic_data.get('user_id', 'anonymous')
            user_dir = self.storage_dir / user_id
            user_dir.mkdir(exist_ok=True)
            
            file_path = user_dir / f"{diagnostic_data['id']}.json"
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(diagnostic_data, file, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar diagnóstico em disco: {e}")
    
    def get_by_id(self, diagnostic_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Recupera um diagnóstico pelo ID
        
        Args:
            diagnostic_id: ID do diagnóstico
            user_id: ID do usuário (se None, busca em todos os usuários)
            
        Returns:
            Dados do diagnóstico ou None se não encontrado
        """
        # Se o usuário for especificado, busca apenas nele
        if user_id:
            for diagnostic in self._diagnostics.get(user_id, []):
                if diagnostic.get('id') == diagnostic_id:
                    return diagnostic
            
            # Tenta buscar no disco
            if self.storage_path:
                return self._load_from_disk(diagnostic_id, user_id)
            
            return None
        
        # Busca em todos os usuários
        for user_diagnostics in self._diagnostics.values():
            for diagnostic in user_diagnostics:
                if diagnostic.get('id') == diagnostic_id:
                    return diagnostic
        
        # Tenta buscar no disco
        if self.storage_path:
            return self._load_from_disk(diagnostic_id)
        
        return None
    
    def _load_from_disk(self, diagnostic_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Carrega um diagnóstico do disco
        
        Args:
            diagnostic_id: ID do diagnóstico
            user_id: ID do usuário (se None, busca em todos os usuários)
            
        Returns:
            Dados do diagnóstico ou None se não encontrado
        """
        try:
            if user_id:
                # Busca apenas no diretório do usuário
                file_path = self.storage_dir / user_id / f"{diagnostic_id}.json"
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as file:
                        return json.load(file)
            else:
                # Busca em todos os diretórios de usuários
                for user_dir in self.storage_dir.iterdir():
                    if user_dir.is_dir():
                        file_path = user_dir / f"{diagnostic_id}.json"
                        if file_path.exists():
                            with open(file_path, 'r', encoding='utf-8') as file:
                                return json.load(file)
        except Exception as e:
            logger.error(f"Erro ao carregar diagnóstico do disco: {e}")
        
        return None
    
    def get_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Recupera o histórico de diagnósticos para um usuário
        
        Args:
            user_id: ID do usuário
            limit: Limite de registros
            
        Returns:
            Lista de diagnósticos resumidos
        """
        history = []
        
        # Recupera da memória
        for diagnostic in self._diagnostics.get(user_id, []):
            history.append({
                'id': diagnostic.get('id'),
                'timestamp': diagnostic.get('timestamp'),
                'score': diagnostic.get('score'),
                'problems_count': len(diagnostic.get('problems', []))
            })
        
        # Carrega do disco se configurado
        if self.storage_path and len(history) < limit:
            disk_history = self._load_history_from_disk(user_id, limit - len(history))
            history.extend(disk_history)
        
        # Ordena por timestamp (mais recente primeiro)
        history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return history[:limit]
    
    def _load_history_from_disk(self, user_id: str, limit: int) -> List[Dict[str, Any]]:
        """
        Carrega histórico de diagnósticos do disco
        
        Args:
            user_id: ID do usuário
            limit: Limite de registros
            
        Returns:
            Lista de diagnósticos resumidos
        """
        history = []
        try:
            user_dir = self.storage_dir / user_id
            if user_dir.exists():
                # Lista todos os arquivos JSON no diretório do usuário
                json_files = list(user_dir.glob('*.json'))
                
                # Limita a quantidade de arquivos a processar para evitar sobrecarga
                for file_path in json_files[:limit*2]:  # 2x para caso alguns não sejam válidos
                    if len(history) >= limit:
                        break
                        
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            data = json.load(file)
                            # Extrai apenas os campos necessários para o histórico
                            history.append({
                                'id': data.get('id'),
                                'timestamp': data.get('timestamp'),
                                'score': data.get('score'),
                                'problems_count': len(data.get('problems', []))
                            })
                    except Exception as e:
                        logger.warning(f"Erro ao carregar arquivo {file_path}: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Erro ao carregar histórico do disco: {e}")
        
        return history[:limit]
    
    def get_all(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Recupera todos os diagnósticos
        
        Args:
            limit: Limite opcional de registros
            
        Returns:
            Lista de todos os diagnósticos resumidos
        """
        all_diagnostics = []
        
        # Recupera da memória
        for user_diagnostics in self._diagnostics.values():
            for diagnostic in user_diagnostics:
                all_diagnostics.append({
                    'id': diagnostic.get('id'),
                    'user_id': diagnostic.get('user_id', 'anonymous'),
                    'timestamp': diagnostic.get('timestamp'),
                    'score': diagnostic.get('score'),
                    'problems_count': len(diagnostic.get('problems', []))
                })
        
        # Carrega do disco se configurado
        if self.storage_path and (limit is None or len(all_diagnostics) < limit):
            disk_limit = None if limit is None else limit - len(all_diagnostics)
            disk_diagnostics = self._load_all_from_disk(disk_limit)
            all_diagnostics.extend(disk_diagnostics)
        
        # Ordena por timestamp (mais recente primeiro)
        all_diagnostics.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Aplica limite se especificado
        if limit is not None:
            all_diagnostics = all_diagnostics[:limit]
            
        # Libera memória explicitamente após a operação
        if len(all_diagnostics) > 100:  # Threshold arbitrário para operações grandes
            gc.collect()
            
        return all_diagnostics
    
    def _load_all_from_disk(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Carrega todos os diagnósticos do disco
        
        Args:
            limit: Limite opcional de registros
            
        Returns:
            Lista de todos os diagnósticos resumidos
        """
        all_diagnostics = []
        try:
            if not self.storage_dir.exists():
                return all_diagnostics
                
            # Para cada diretório de usuário
            for user_dir in self.storage_dir.iterdir():
                if not user_dir.is_dir():
                    continue
                    
                user_id = user_dir.name
                
                # Lista todos os arquivos JSON no diretório do usuário
                json_files = list(user_dir.glob('*.json'))
                
                # Aplica limite se especificado
                processed_files = 0
                for file_path in json_files:
                    if limit is not None and len(all_diagnostics) >= limit:
                        break
                        
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            data = json.load(file)
                            # Extrai apenas os campos necessários
                            all_diagnostics.append({
                                'id': data.get('id'),
                                'user_id': user_id,
                                'timestamp': data.get('timestamp'),
                                'score': data.get('score'),
                                'problems_count': len(data.get('problems', []))
                            })
                    except Exception as e:
                        logger.warning(f"Erro ao carregar arquivo {file_path}: {e}")
                        
                    # Incrementa contador de arquivos processados
                    processed_files += 1
                    
                    # A cada 100 arquivos processados, verifica se precisa liberar memória
                    if processed_files % 100 == 0:
                        gc.collect()
                        
        except Exception as e:
            logger.error(f"Erro ao carregar todos os diagnósticos do disco: {e}")
        
        return all_diagnostics
    
    def get_count(self, user_id: Optional[str] = None) -> int:
        """
        Retorna a quantidade de diagnósticos
        
        Args:
            user_id: ID opcional do usuário para filtrar
            
        Returns:
            Quantidade de diagnósticos
        """
        # Conta da memória
        if user_id:
            count = len(self._diagnostics.get(user_id, []))
        else:
            count = sum(len(diagnostics) for diagnostics in self._diagnostics.values())
        
        # Conta do disco
        if self.storage_path:
            try:
                if user_id:
                    # Conta apenas para o usuário especificado
                    user_dir = self.storage_dir / user_id
                    if user_dir.exists():
                        count += len(list(user_dir.glob('*.json')))
                else:
                    # Conta para todos os usuários
                    for user_dir in self.storage_dir.iterdir():
                        if user_dir.is_dir():
                            count += len(list(user_dir.glob('*.json')))
            except Exception as e:
                logger.error(f"Erro ao contar diagnósticos no disco: {e}")
        
        return count
        
    def clear_cache(self):
        """
        Limpa o cache de diagnósticos em memória
        """
        self._diagnostics.clear()
        gc.collect()
        logger.info("Cache de diagnósticos limpo")
        
    def save_diagnostic(self, diagnostic_data: Dict[str, Any]) -> str:
        """
        Salva um diagnóstico (alias para o método save para compatibilidade)
        
        Args:
            diagnostic_data: Dados do diagnóstico
            
        Returns:
            ID do diagnóstico salvo
        """
        return self.save(diagnostic_data) 