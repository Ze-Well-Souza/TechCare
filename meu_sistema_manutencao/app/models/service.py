from app.extensions import db
from datetime import datetime
import psutil
import subprocess
import platform

class Service(db.Model):
    """
    Modelo para representar serviços do sistema
    """
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='stopped')
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    pid = db.Column(db.Integer, nullable=True)
    
    def update_status(self):
        """
        Atualiza o status do serviço
        """
        try:
            if self.pid:
                # Verificar se o processo ainda está em execução
                if platform.system() == 'Windows':
                    process = subprocess.run(['tasklist', '/FI', f'PID eq {self.pid}'], 
                                             capture_output=True, text=True)
                    self.status = 'running' if process.returncode == 0 else 'stopped'
                else:
                    try:
                        os.kill(self.pid, 0)
                        self.status = 'running'
                    except OSError:
                        self.status = 'stopped'
            
            self.last_updated = datetime.utcnow()
            db.session.commit()
        except Exception as e:
            self.status = 'error'
            db.session.commit()
            raise

    def start(self):
        """
        Iniciar o serviço
        """
        try:
            # Lógica específica para iniciar o serviço
            # Exemplo genérico, deve ser substituído por lógica específica
            process = subprocess.Popen([self.name])
            self.pid = process.pid
            self.status = 'running'
            self.last_updated = datetime.utcnow()
            db.session.commit()
        except Exception as e:
            self.status = 'error'
            db.session.commit()
            raise

    def stop(self):
        """
        Parar o serviço
        """
        try:
            if self.pid:
                if platform.system() == 'Windows':
                    subprocess.run(['taskkill', '/F', '/PID', str(self.pid)])
                else:
                    os.kill(self.pid, signal.SIGTERM)
                
            self.pid = None
            self.status = 'stopped'
            self.last_updated = datetime.utcnow()
            db.session.commit()
        except Exception as e:
            self.status = 'error'
            db.session.commit()
            raise

    def to_dict(self):
        """
        Converte o serviço para dicionário
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'pid': self.pid
        }

    @classmethod
    def get_system_services(cls):
        """
        Obtém lista de serviços do sistema
        """
        services = []
        
        # Serviços de exemplo, deve ser adaptado conforme necessidade
        system_services = [
            {'name': 'nginx', 'description': 'Servidor web'},
            {'name': 'postgresql', 'description': 'Banco de dados'},
            {'name': 'redis', 'description': 'Cache e fila de mensagens'}
        ]
        
        for service_info in system_services:
            existing_service = cls.query.filter_by(name=service_info['name']).first()
            
            if not existing_service:
                new_service = cls(
                    name=service_info['name'], 
                    description=service_info['description']
                )
                db.session.add(new_service)
        
        db.session.commit()
        return cls.query.all()
