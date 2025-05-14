import os
import sys
import sqlite3
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def update_database(db_path):
    """
    Atualiza um único banco de dados.
    """
    logger.info(f"Atualizando esquema do banco de dados em: {db_path}")
    
    # Conectar ao banco de dados
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar se a tabela roles existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='roles'")
        if not cursor.fetchone():
            logger.info(f"Criando tabela roles em {db_path}...")
            cursor.execute('''
            CREATE TABLE roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(64) UNIQUE,
                description VARCHAR(255),
                permissions INTEGER DEFAULT 0
            )
            ''')
            
            # Inserir roles padrão
            cursor.execute('''
            INSERT INTO roles (name, description, permissions) VALUES 
            ('Admin Master', 'Acesso completo ao sistema', 63),
            ('Técnico', 'Acesso a funcionalidades técnicas', 15),
            ('Visualizador', 'Acesso somente leitura', 3)
            ''')
            logger.info(f"Tabela roles criada com sucesso em {db_path}.")
        else:
            logger.info(f"Tabela roles já existe em {db_path}.")
        
        # Verificar se a coluna role_id existe na tabela users
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'role_id' not in columns:
            logger.info(f"Adicionando coluna role_id à tabela users em {db_path}...")
            cursor.execute("ALTER TABLE users ADD COLUMN role_id INTEGER REFERENCES roles(id)")
            logger.info(f"Coluna role_id adicionada com sucesso em {db_path}.")
        else:
            logger.info(f"Coluna role_id já existe na tabela users em {db_path}.")
        
        # Commit das alterações
        conn.commit()
        logger.info(f"Esquema do banco de dados atualizado com sucesso em {db_path}.")
        return True
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Erro ao atualizar o esquema do banco de dados {db_path}: {e}")
        return False
    finally:
        conn.close()

def update_database_schema():
    """
    Atualiza o esquema do banco de dados para suportar o sistema de roles.
    Adiciona a coluna role_id à tabela users e cria a tabela roles se necessário.
    Atualiza todos os bancos de dados encontrados.
    """
    # Caminhos potenciais do banco de dados
    db_paths = [
        'instance/techcare-dev.db',
        'instance/techcare-test.db',
        'instance/app.db',
        'instance/techcare.db',
        'app/instance/app.db',
        'app/instance/techcare.db',
        'app.db',
        'techcare.db'
    ]
    
    # Encontrar todos os caminhos de banco de dados que existem
    existing_dbs = []
    for path in db_paths:
        if os.path.exists(path):
            existing_dbs.append(path)
    
    if not existing_dbs:
        logger.error("Banco de dados não encontrado em nenhum dos caminhos esperados.")
        sys.exit(1)
    
    # Atualizar todos os bancos de dados encontrados
    success_count = 0
    for db_path in existing_dbs:
        if update_database(db_path):
            success_count += 1
    
    if success_count == len(existing_dbs):
        logger.info(f"Todos os {success_count} bancos de dados foram atualizados com sucesso.")
    else:
        logger.warning(f"Apenas {success_count} de {len(existing_dbs)} bancos de dados foram atualizados com sucesso.")

if __name__ == "__main__":
    update_database_schema() 