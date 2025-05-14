import json
from datetime import datetime

from app import db

class Diagnostic(db.Model):
    """Modelo para armazenar resultados de diagnósticos"""
    __tablename__ = 'diagnostics'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(64))  # Nome do diagnóstico ou do computador
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Resultados de cada componente analisado
    cpu_results = db.Column(db.Text)  # JSON com resultados da CPU
    memory_results = db.Column(db.Text)  # JSON com resultados da memória
    disk_results = db.Column(db.Text)  # JSON com resultados do disco
    startup_results = db.Column(db.Text)  # JSON com resultados dos programas de inicialização
    driver_results = db.Column(db.Text)  # JSON com resultados dos drivers
    security_results = db.Column(db.Text)  # JSON com resultados de segurança
    network_results = db.Column(db.Text)  # JSON com resultados da rede
    
    # Pontuação e status geral
    score = db.Column(db.Float)  # Pontuação geral (0-100)
    status = db.Column(db.String(20))  # Bom, Regular, Crítico
    
    # Recomendações e observações
    recommendations = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Alias para compatibilidade com testes
    @property
    def timestamp(self):
        """Alias para date, para compatibilidade com testes"""
        return self.date
    
    def set_cpu_results(self, data):
        """Converte os resultados da CPU para formato JSON"""
        self.cpu_results = json.dumps(data)
    
    def get_cpu_results(self):
        """Obtém os resultados da CPU como dicionário"""
        return json.loads(self.cpu_results) if self.cpu_results else {}
    
    def set_memory_results(self, data):
        """Converte os resultados da memória para formato JSON"""
        self.memory_results = json.dumps(data)
    
    def get_memory_results(self):
        """Obtém os resultados da memória como dicionário"""
        return json.loads(self.memory_results) if self.memory_results else {}
    
    def set_disk_results(self, data):
        """Converte os resultados do disco para formato JSON"""
        self.disk_results = json.dumps(data)
    
    def get_disk_results(self):
        """Obtém os resultados do disco como dicionário"""
        return json.loads(self.disk_results) if self.disk_results else {}
    
    def set_startup_results(self, data):
        """Converte os resultados dos programas de inicialização para formato JSON"""
        self.startup_results = json.dumps(data)
    
    def get_startup_results(self):
        """Obtém os resultados dos programas de inicialização como dicionário"""
        return json.loads(self.startup_results) if self.startup_results else {}
    
    def set_driver_results(self, data):
        """Converte os resultados dos drivers para formato JSON"""
        self.driver_results = json.dumps(data)
    
    def get_driver_results(self):
        """Obtém os resultados dos drivers como dicionário"""
        return json.loads(self.driver_results) if self.driver_results else {}
    
    def set_security_results(self, data):
        """Converte os resultados de segurança para formato JSON"""
        self.security_results = json.dumps(data)
    
    def get_security_results(self):
        """Obtém os resultados de segurança como dicionário"""
        return json.loads(self.security_results) if self.security_results else {}
    
    def set_network_results(self, data):
        """Converte os resultados da rede para formato JSON"""
        self.network_results = json.dumps(data)
    
    def get_network_results(self):
        """Obtém os resultados da rede como dicionário"""
        return json.loads(self.network_results) if self.network_results else {}
    
    def __repr__(self):
        return f'<Diagnostic {self.name} - {self.date}>' 