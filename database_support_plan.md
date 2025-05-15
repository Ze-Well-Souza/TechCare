# Plano de Implementação de Suporte a Múltiplos Bancos de Dados

## Visão Geral

Atualmente, o TechCare usa SQLite como banco de dados principal, o que é ideal para implantações simples e desenvolvimento. No entanto, para maior escalabilidade e em ambientes de produção mais robustos, é necessário implementar suporte a outros bancos de dados relacionais como PostgreSQL e MySQL.

## Objetivos

- Implementar suporte completo para PostgreSQL
- Implementar suporte para MySQL/MariaDB
- Criar scripts de migração entre diferentes bancos
- Manter compatibilidade com SQLite para desenvolvimento e implantações menores
- Garantir que todas as consultas e operações funcionem consistentemente em todos os bancos suportados

## Arquitetura Atual

Atualmente, o TechCare utiliza SQLAlchemy como ORM com uma configuração básica para SQLite:

```python
# config.py
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'techcare.db')
```

O SQLAlchemy já oferece suporte a vários bancos de dados, o que facilita a implementação.

## Estratégia de Implementação

### Fase 1: Refatoração da Configuração do Banco de Dados

1. **Criar Configurações para Múltiplos Bancos**

   ```python
   # config.py
   class Config:
       # ...
       
       @staticmethod
       def get_database_uri(db_type=None):
           """
           Retorna a URI de conexão do banco de dados apropriada.
           Args:
               db_type: Tipo de banco ('sqlite', 'postgresql', 'mysql')
                      Se None, será detectado da variável DB_TYPE ou default para sqlite
           """
           db_type = db_type or os.environ.get('DB_TYPE', 'sqlite')
           db_type = db_type.lower()
           
           if db_type == 'sqlite':
               return os.environ.get('DATABASE_URL') or \
                   'sqlite:///' + os.path.join(Config.BASE_DIR, 'instance', 'techcare.db')
           
           elif db_type == 'postgresql':
               user = os.environ.get('DB_USER', 'techcare')
               password = os.environ.get('DB_PASSWORD', 'techcare')
               host = os.environ.get('DB_HOST', 'localhost')
               port = os.environ.get('DB_PORT', '5432')
               name = os.environ.get('DB_NAME', 'techcare')
               return f'postgresql://{user}:{password}@{host}:{port}/{name}'
           
           elif db_type == 'mysql':
               user = os.environ.get('DB_USER', 'techcare')
               password = os.environ.get('DB_PASSWORD', 'techcare')
               host = os.environ.get('DB_HOST', 'localhost')
               port = os.environ.get('DB_PORT', '3306')
               name = os.environ.get('DB_NAME', 'techcare')
               return f'mysql+pymysql://{user}:{password}@{host}:{port}/{name}'
           
           else:
               raise ValueError(f"Tipo de banco de dados não suportado: {db_type}")
   
   # Atualizar as classes de configuração para usar o método
   class DevelopmentConfig(Config):
       # ...
       SQLALCHEMY_DATABASE_URI = Config.get_database_uri()
   
   class TestingConfig(Config):
       # ...
       SQLALCHEMY_DATABASE_URI = Config.get_database_uri('sqlite')  # Sempre sqlite para testes
   
   class ProductionConfig(Config):
       # ...
       SQLALCHEMY_DATABASE_URI = Config.get_database_uri(os.environ.get('DB_TYPE', 'postgresql'))
   ```

2. **Criar Fábrica de Conexão de Banco de Dados**

   ```python
   # app/utils/db_factory.py
   from sqlalchemy import create_engine
   from sqlalchemy.orm import sessionmaker
   
   def get_db_engine(db_uri):
       """Cria e retorna um engine SQLAlchemy para a URI fornecida"""
       return create_engine(db_uri)
   
   def get_db_session(engine):
       """Cria e retorna uma sessão SQLAlchemy para o engine fornecido"""
       Session = sessionmaker(bind=engine)
       return Session()
   ```

### Fase 2: Adaptar Modelos e Migrações

1. **Verificar Compatibilidade de Tipos**

   Revisar todos os modelos para garantir que os tipos de dados sejam compatíveis com todos os bancos suportados:

   ```python
   # app/models/user.py
   # Antes
   class User(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       username = db.Column(db.String(64), unique=True)
       # ...
       
   # Depois - com tipos mais específicos
   class User(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       username = db.Column(db.String(64), unique=True, nullable=False)
       # ...
   ```

2. **Implementar Alembic para Migrações**

   ```python
   # migrations/env.py
   # Configuração para Alembic
   from alembic import context
   from app import db
   
   target_metadata = db.metadata
   
   # Configurar URL
   config.set_main_option('sqlalchemy.url', config.get_main_option('sqlalchemy.url'))
   ```

3. **Criar Scripts de Migração Base**

   ```bash
   # Inicializar Alembic
   flask db init
   
   # Criar migração inicial
   flask db migrate -m "Estrutura inicial do banco de dados"
   ```

### Fase 3: Implementar Scripts de Utilitário

1. **Script para Migração entre Bancos de Dados**

   ```python
   # scripts/migrate_database.py
   import os
   import sys
   import argparse
   from sqlalchemy import create_engine
   from app.config import Config
   
   def migrate_database(source_type, target_type, dump_file=None):
       """Migra dados de um tipo de banco para outro"""
       source_uri = Config.get_database_uri(source_type)
       target_uri = Config.get_database_uri(target_type)
       
       print(f"Migrando dados de {source_type} para {target_type}")
       
       # Usar SQLAlchemy para ler todos os dados
       source_engine = create_engine(source_uri)
       
       # Criar conexão com banco destino
       target_engine = create_engine(target_uri)
       
       # Implementar lógica de migração adequada
       # ...
   
   if __name__ == "__main__":
       parser = argparse.ArgumentParser(description='Migrar banco de dados TechCare')
       parser.add_argument('--source', required=True, choices=['sqlite', 'postgresql', 'mysql'],
                           help='Tipo de banco de dados de origem')
       parser.add_argument('--target', required=True, choices=['sqlite', 'postgresql', 'mysql'],
                           help='Tipo de banco de dados de destino')
       parser.add_argument('--dump', help='Caminho para arquivo de dump (opcional)')
       
       args = parser.parse_args()
       migrate_database(args.source, args.target, args.dump)
   ```

2. **Script para Verificação de Compatibilidade**

   ```python
   # scripts/check_db_compatibility.py
   from sqlalchemy import inspect
   from app.config import Config
   from app import db, models
   import importlib
   
   def check_compatibility(db_type):
       """Verifica a compatibilidade dos modelos com o banco especificado"""
       db_uri = Config.get_database_uri(db_type)
       engine = db.create_engine(db_uri)
       inspector = inspect(engine)
       
       # Verificar se todas as tabelas existem
       tables = inspector.get_table_names()
       
       # Obter todos os modelos
       all_models = []
       for module_name in dir(models):
           module = getattr(models, module_name)
           for attr_name in dir(module):
               attr = getattr(module, attr_name)
               if hasattr(attr, '__tablename__'):
                   all_models.append(attr)
       
       # Verificar se cada modelo tem uma tabela correspondente
       missing_tables = []
       for model in all_models:
           if model.__tablename__ not in tables:
               missing_tables.append(model.__tablename__)
       
       # Verificar colunas em cada tabela
       column_issues = {}
       for model in all_models:
           if model.__tablename__ in tables:
               db_columns = {c['name'] for c in inspector.get_columns(model.__tablename__)}
               model_columns = {c.name for c in model.__table__.columns}
               
               missing_in_db = model_columns - db_columns
               extra_in_db = db_columns - model_columns
               
               if missing_in_db or extra_in_db:
                   column_issues[model.__tablename__] = {
                       'missing_in_db': list(missing_in_db),
                       'extra_in_db': list(extra_in_db)
                   }
       
       return {
           'missing_tables': missing_tables,
           'column_issues': column_issues
       }
   ```

### Fase 4: Otimizações Específicas para Cada Banco

1. **Implementar Otimizações para PostgreSQL**

   ```python
   # app/utils/db_optimizations.py
   def optimize_for_postgres(db):
       """Aplica otimizações específicas para PostgreSQL"""
       if 'postgresql' in str(db.engine.url):
           # Configurar índices específicos do PostgreSQL
           with db.engine.connect() as conn:
               conn.execute("SET work_mem = '16MB'")
               conn.execute("SET maintenance_work_mem = '128MB'")
   ```

2. **Implementar Otimizações para MySQL**

   ```python
   # app/utils/db_optimizations.py
   def optimize_for_mysql(db):
       """Aplica otimizações específicas para MySQL"""
       if 'mysql' in str(db.engine.url):
           # Configurar otimizações específicas do MySQL
           with db.engine.connect() as conn:
               conn.execute("SET innodb_buffer_pool_size = 256M")
               conn.execute("SET innodb_flush_log_at_trx_commit = 2")
   ```

### Fase 5: Testes e Validação

1. **Testes Automatizados para Cada Banco**

   ```python
   # tests/test_db_compatibility.py
   import pytest
   from app import create_app, db
   from app.config import Config
   
   @pytest.fixture
   def app_sqlite():
       app = create_app('testing')
       with app.app_context():
           db.create_all()
           yield app
           db.drop_all()
   
   @pytest.fixture
   def app_postgres():
       old_uri = Config.TestingConfig.SQLALCHEMY_DATABASE_URI
       Config.TestingConfig.SQLALCHEMY_DATABASE_URI = Config.get_database_uri('postgresql')
       app = create_app('testing')
       with app.app_context():
           db.create_all()
           yield app
           db.drop_all()
       Config.TestingConfig.SQLALCHEMY_DATABASE_URI = old_uri
   
   def test_user_model_sqlite(app_sqlite):
       # Testar modelo User no SQLite
       # ...
   
   def test_user_model_postgres(app_postgres):
       # Testar modelo User no PostgreSQL
       # ...
   ```

2. **Testes de Desempenho**

   ```python
   # tests/test_db_performance.py
   import time
   import pytest
   from app import create_app, db
   from app.models import User, Diagnostic
   
   def measure_performance(app, num_records=1000):
       """Mede desempenho de operações básicas de banco de dados"""
       results = {}
       with app.app_context():
           # Medir inserção
           start = time.time()
           for i in range(num_records):
               user = User(username=f'testuser{i}', email=f'test{i}@example.com')
               db.session.add(user)
           db.session.commit()
           results['insert'] = time.time() - start
           
           # Medir consulta
           start = time.time()
           for i in range(num_records):
               User.query.filter_by(username=f'testuser{i}').first()
           results['query'] = time.time() - start
           
           # Limpar
           User.query.delete()
           db.session.commit()
           
       return results
   ```

## Plano de Migração para Instalações Existentes

### 1. Script de Detecção e Backup

```python
# scripts/prepare_migration.py
import os
import datetime
import shutil
from app.config import Config

def prepare_migration():
    """Prepara para migração detectando banco atual e criando backup"""
    # Detectar banco atual
    db_uri = Config.get_database_uri()
    db_type = 'sqlite'
    
    if 'postgresql' in db_uri:
        db_type = 'postgresql'
    elif 'mysql' in db_uri:
        db_type = 'mysql'
    
    print(f"Banco atual detectado: {db_type}")
    
    # Criar backup
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if db_type == 'sqlite':
        db_path = os.path.join(Config.BASE_DIR, 'instance', 'techcare.db')
        backup_path = os.path.join(Config.BASE_DIR, 'backups', f'techcare_{timestamp}.db')
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        shutil.copy2(db_path, backup_path)
        print(f"Backup criado em: {backup_path}")
    else:
        # Para PostgreSQL e MySQL, usar comandos específicos de backup
        backup_file = os.path.join(Config.BASE_DIR, 'backups', f'techcare_{db_type}_{timestamp}.sql')
        os.makedirs(os.path.dirname(backup_file), exist_ok=True)
        
        if db_type == 'postgresql':
            # Usar pg_dump
            db_name = os.environ.get('DB_NAME', 'techcare')
            db_user = os.environ.get('DB_USER', 'techcare')
            db_host = os.environ.get('DB_HOST', 'localhost')
            os.system(f'pg_dump -U {db_user} -h {db_host} -d {db_name} -f {backup_file}')
        elif db_type == 'mysql':
            # Usar mysqldump
            db_name = os.environ.get('DB_NAME', 'techcare')
            db_user = os.environ.get('DB_USER', 'techcare')
            db_password = os.environ.get('DB_PASSWORD', 'techcare')
            db_host = os.environ.get('DB_HOST', 'localhost')
            os.system(f'mysqldump -u {db_user} -p{db_password} -h {db_host} {db_name} > {backup_file}')
        
        print(f"Backup criado em: {backup_file}")
        
    return db_type, backup_file
```

### 2. Plano de Rollback

Sempre ter um plano de rollback é crucial. Criar scripts que possam restaurar o banco anterior em caso de problemas:

```python
# scripts/rollback_migration.py
import os
import argparse
from app.config import Config

def rollback_migration(backup_file, db_type):
    """Restaura um backup em caso de problemas na migração"""
    # Implementar lógica de restauração baseada no tipo de banco
    if db_type == 'sqlite':
        db_path = os.path.join(Config.BASE_DIR, 'instance', 'techcare.db')
        os.replace(backup_file, db_path)
        print(f"Banco SQLite restaurado de: {backup_file}")
    elif db_type == 'postgresql':
        # Restaurar PostgreSQL
        db_name = os.environ.get('DB_NAME', 'techcare')
        db_user = os.environ.get('DB_USER', 'techcare')
        db_host = os.environ.get('DB_HOST', 'localhost')
        os.system(f'psql -U {db_user} -h {db_host} -d {db_name} -f {backup_file}')
        print(f"Banco PostgreSQL restaurado de: {backup_file}")
    elif db_type == 'mysql':
        # Restaurar MySQL
        db_name = os.environ.get('DB_NAME', 'techcare')
        db_user = os.environ.get('DB_USER', 'techcare')
        db_password = os.environ.get('DB_PASSWORD', 'techcare')
        db_host = os.environ.get('DB_HOST', 'localhost')
        os.system(f'mysql -u {db_user} -p{db_password} -h {db_host} {db_name} < {backup_file}')
        print(f"Banco MySQL restaurado de: {backup_file}")
```

## Adequações para Produção

### 1. Configuração de Conexões para Produção

Para ambientes de produção, configurações adicionais são necessárias:

```python
# Expandir a configuração para produção
class ProductionConfig(Config):
    # ...
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'connect_args': {
            'connect_timeout': 10
        }
    }
```

### 2. Configuração de Healthcheck e Monitoramento

```python
# app/routes/api.py
@bp.route('/health/db', methods=['GET'])
@auth_required
def db_health():
    """Verifica saúde da conexão com banco de dados"""
    try:
        # Tentar execução simples
        result = db.session.execute('SELECT 1').scalar()
        if result == 1:
            return jsonify({
                'status': 'ok',
                'db_type': db.engine.name,
                'db_version': db.session.execute('SELECT VERSION()').scalar()
            })
        return jsonify({
            'status': 'error',
            'message': 'Verificação do banco de dados falhou'
        }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
```

## Requisitos de Dependências

Atualizar o requirements.txt para incluir as dependências necessárias:

```text
# requirements.txt
flask==3.1.0
sqlalchemy==2.0.32
flask-sqlalchemy==3.1.0
flask-migrate==4.0.5
alembic==1.12.1
# Drivers de banco de dados
psycopg2-binary==2.9.9  # PostgreSQL
pymysql==1.1.0  # MySQL
cryptography==42.0.5  # Para MySQL+SSL
```

## Cronograma de Implementação

1. **Fase 1**: Refatoração da Configuração (1 semana)
2. **Fase 2**: Adaptação de Modelos e Migrações (2 semanas)
3. **Fase 3**: Scripts de Utilitário (1 semana)
4. **Fase 4**: Otimizações Específicas (1 semana)
5. **Fase 5**: Testes e Validação (2 semanas)

**Total**: 7 semanas

## Riscos e Mitigação

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Incompatibilidade de tipos de dados | Média | Alto | Revisar todos os modelos e usar tipos compatíveis com todos os bancos |
| Falha na migração de dados | Média | Crítico | Implementar backups automáticos e plano de rollback |
| Problemas de desempenho | Média | Alto | Testes de carga e otimizações específicas para cada banco |
| Problemas de configuração em produção | Alta | Médio | Documentação detalhada e scripts de verificação pré-migração |

## Documentação

Será necessário atualizar a documentação para incluir:

1. Guia de instalação para cada banco de dados
2. Procedimentos de migração entre bancos
3. Instruções de backup e recuperação
4. Procedimentos de monitoramento e manutenção 