# Guia de Implantação do TechCare

Este guia apresenta instruções detalhadas para implantar o aplicativo TechCare em um ambiente de produção seguro e escalável.

## Requisitos de Sistema

- **Sistema Operacional**: Linux (recomendado Ubuntu 20.04 LTS ou superior)
- **Python**: 3.8 ou superior
- **Banco de Dados**: PostgreSQL 12 ou superior
- **Servidor Web**: Nginx
- **Processador WSGI**: Gunicorn

## 1. Preparação do Servidor

### 1.1 Atualização do Sistema

```bash
sudo apt update
sudo apt upgrade -y
```

### 1.2 Instalação de Dependências

```bash
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev
```

### 1.3 Criação de Usuário de Serviço

```bash
sudo useradd -m -s /bin/bash techcare
sudo usermod -aG sudo techcare
```

## 2. Configuração do Banco de Dados

### 2.1 Criar Usuário e Banco de Dados

```bash
sudo -u postgres psql

CREATE USER techcare WITH PASSWORD 'senha_segura';
CREATE DATABASE techcare_production;
GRANT ALL PRIVILEGES ON DATABASE techcare_production TO techcare;
\q
```

### 2.2 Configurar Acesso ao Banco de Dados

Edite o arquivo `/etc/postgresql/12/main/pg_hba.conf` (substitua "12" pela sua versão) para permitir o acesso local:

```
local   techcare_production    techcare                               md5
host    techcare_production    techcare         127.0.0.1/32          md5
host    techcare_production    techcare         ::1/128               md5
```

Reinicie o PostgreSQL:

```bash
sudo systemctl restart postgresql
```

## 3. Implantação da Aplicação

### 3.1 Clonar o Repositório

```bash
sudo -u techcare -i
git clone https://github.com/seu-usuario/techcare.git /home/techcare/app
cd /home/techcare/app
```

### 3.2 Configurar Ambiente Virtual

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### 3.3 Configurar Variáveis de Ambiente

Crie um arquivo `.env` para armazenar variáveis de ambiente:

```bash
touch /home/techcare/app/.env
```

Edite o arquivo com as configurações necessárias:

```
FLASK_APP=wsgi.py
FLASK_ENV=production
SECRET_KEY=gere_uma_chave_secreta_aleatoria
DATABASE_URL=postgresql://techcare:senha_segura@localhost/techcare_production
SERVER_NAME=seu-dominio.com
ADMIN_EMAIL=admin@seu-dominio.com
```

### 3.4 Inicializar o Banco de Dados

```bash
cd /home/techcare/app
flask db upgrade
flask seed-admin  # Se existir um comando para criar o usuário admin inicial
```

## 4. Configuração do Gunicorn

### 4.1 Criar Script de Inicialização

Já existe um script de inicialização em `scripts/start_gunicorn.sh`. Certifique-se de que ele tenha permissão de execução:

```bash
chmod +x /home/techcare/app/scripts/start_gunicorn.sh
```

### 4.2 Criar Serviço Systemd

Crie um arquivo de serviço Systemd para gerenciar o Gunicorn:

```bash
sudo nano /etc/systemd/system/techcare.service
```

Adicione o seguinte conteúdo:

```ini
[Unit]
Description=TechCare Gunicorn Server
After=network.target postgresql.service

[Service]
User=techcare
Group=techcare
WorkingDirectory=/home/techcare/app
Environment="PATH=/home/techcare/app/venv/bin"
EnvironmentFile=/home/techcare/app/.env
ExecStart=/home/techcare/app/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Ative e inicie o serviço:

```bash
sudo systemctl daemon-reload
sudo systemctl enable techcare
sudo systemctl start techcare
```

## 5. Configuração do Nginx

### 5.1 Criar Configuração do Nginx

Uma configuração de exemplo está disponível em `config/nginx/techcare.conf`. Copie-a para o diretório do Nginx:

```bash
sudo cp /home/techcare/app/config/nginx/techcare.conf /etc/nginx/sites-available/techcare
```

Edite o arquivo para substituir `example.com` pelo seu domínio real e atualizar os caminhos dos certificados SSL.

### 5.2 Ativar o Site

```bash
sudo ln -s /etc/nginx/sites-available/techcare /etc/nginx/sites-enabled/
sudo nginx -t  # Testar a configuração
sudo systemctl restart nginx
```

### 5.3 Configurar SSL com Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com
```

## 6. Configuração de Segurança

### 6.1 Configurar Firewall

```bash
sudo apt install -y ufw
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
```

### 6.2 Configurar Backups Automáticos

Crie um script para backup do banco de dados:

```bash
sudo nano /home/techcare/app/scripts/backup.sh
```

Adicione o seguinte conteúdo:

```bash
#!/bin/bash
BACKUP_DIR="/home/techcare/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/techcare_db_$TIMESTAMP.sql"

mkdir -p $BACKUP_DIR
pg_dump -U techcare -d techcare_production > $BACKUP_FILE
gzip $BACKUP_FILE

# Manter apenas os últimos 7 backups
find $BACKUP_DIR -name "techcare_db_*.sql.gz" -type f -mtime +7 -delete
```

Torne o script executável e configure um cron job:

```bash
chmod +x /home/techcare/app/scripts/backup.sh
sudo crontab -e
```

Adicione a seguinte linha para fazer backup diário às 2 da manhã:

```
0 2 * * * /home/techcare/app/scripts/backup.sh
```

## 7. Monitoramento e Logging

### 7.1 Configurar Rotação de Logs

O sistema já está configurado para usar o RotatingFileHandler para logs da aplicação. Os logs serão armazenados em `/var/log/techcare/`.

### 7.2 Monitoramento da Aplicação

Para monitoramento básico, você pode usar o SystemD:

```bash
sudo systemctl status techcare
```

Para um monitoramento mais avançado, considere a instalação de ferramentas como Prometheus, Grafana ou Sentry.

## 8. Manutenção Contínua

### 8.1 Atualizações da Aplicação

```bash
cd /home/techcare/app
sudo systemctl stop techcare
git pull
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade
sudo systemctl start techcare
```

### 8.2 Verificação de Logs

Verifique regularmente os logs da aplicação e do Nginx:

```bash
# Logs da aplicação
tail -f /var/log/techcare/info.log
tail -f /var/log/techcare/error.log

# Logs do Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

## 9. Solução de Problemas

### 9.1 A Aplicação Não Inicia

1. Verifique os logs do SystemD:
   ```bash
   sudo journalctl -u techcare.service
   ```

2. Verifique as permissões dos arquivos:
   ```bash
   sudo chown -R techcare:techcare /home/techcare/app
   ```

3. Verifique a conexão com o banco de dados:
   ```bash
   sudo -u techcare -i
   source ~/app/venv/bin/activate
   cd ~/app
   python -c "from app import db; print(db.engine.connect())"
   ```

### 9.2 Erro 502 Bad Gateway

1. Verifique se o Gunicorn está em execução:
   ```bash
   sudo systemctl status techcare
   ```

2. Verifique as configurações do Nginx:
   ```bash
   sudo nginx -t
   ```

3. Reinicie os serviços:
   ```bash
   sudo systemctl restart techcare
   sudo systemctl restart nginx
   ```

## 10. Suporte e Contato

Para obter suporte adicional, entre em contato:

- Email: suporte@techcare.exemplo.com.br
- Site: https://techcare.exemplo.com.br/support 