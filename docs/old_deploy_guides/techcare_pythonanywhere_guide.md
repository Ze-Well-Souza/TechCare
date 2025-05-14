# Guia Rápido: TechCare no PythonAnywhere

## Pré-requisitos
- Conta no PythonAnywhere (gratuita ou paga)
- Token de API (obtido em Account > API Token)
- Python 3.8 ou superior

## Arquivos Importantes
- `README_DEPLOY_PYTHONANYWHERE.md` - Guia detalhado
- `upload_to_pythonanywhere.py` - Script de upload automático
- `check_deploy_readiness.py` - Verificação de prontidão
- `create_deploy_package.py` - Criação de pacote de deploy
- `create_admin_pythonanywhere.py` - Criação de usuário admin

## Deploy Automático (Recomendado)

1. Verificar prontidão:
   ```bash
   python check_deploy_readiness.py
   ```

2. Criar pacote de deploy:
   ```bash
   python create_deploy_package.py
   ```

3. Fazer upload:
   ```bash
   python upload_to_pythonanywhere.py --username SEU_USUARIO --token SEU_TOKEN_API
   ```

## Deploy Manual

1. Verificar prontidão:
   ```bash
   python check_deploy_readiness.py
   ```

2. Criar pacote:
   ```bash
   python create_deploy_package.py
   ```

3. Fazer login no PythonAnywhere e criar um web app Flask.

4. Fazer upload do ZIP e descompactar:
   ```bash
   cd ~
   mkdir TechCare
   cd TechCare
   # Upload via interface Web do PythonAnywhere
   unzip techcare_deploy_package_*.zip
   ```

5. Configurar ambiente virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements_pythonanywhere.txt
   ```

6. Configurar arquivo WSGI e caminhos de arquivo estático.

7. Recarregar a aplicação.

## Comandos Úteis no PythonAnywhere

### Criar Banco de Dados
```bash
cd ~/TechCare
source venv/bin/activate
python -c "from app import create_app, db; app = create_app('production'); app.app_context().push(); db.create_all()"
```

### Criar Usuário Administrador
```bash
cd ~/TechCare
source venv/bin/activate
python create_admin_pythonanywhere.py
```

### Verificar Logs
```bash
# Log de erros da aplicação
tail -f /var/log/your_username.pythonanywhere.com.error.log

# Logs de acesso
tail -f /var/log/your_username.pythonanywhere.com.access.log
```

### Backup do Banco de Dados
```bash
cd ~/TechCare
source venv/bin/activate
python -c "import sqlite3, datetime, shutil; shutil.copy('app.db', f'app_backup_{datetime.datetime.now().strftime(\"%Y%m%d_%H%M%S\")}.db')"
```

## Solução de Problemas Comuns

### Erro 500 (Internal Server Error)
- Verifique os logs de erro
- Certifique-se de que o ambiente virtual está ativado
- Verifique se o banco de dados foi inicializado corretamente

### Erro de Módulo Não Encontrado
- Certifique-se de que todas as dependências estão instaladas
- Verifique se o caminho do projeto está correto no arquivo WSGI

### Arquivos Estáticos Não Carregam
- Verifique a configuração de arquivos estáticos na página Web
- Caminho típico: `/static/` → `/home/your_username/TechCare/app/static`

### Permissões de Arquivo
- Certifique-se de que o banco de dados tem permissões de escrita:
  ```bash
  chmod 666 ~/TechCare/app.db
  ```

## Referências
- [Documentação do PythonAnywhere](https://help.pythonanywhere.com/)
- [Documentação do Flask](https://flask.palletsprojects.com/)
- [Guia Completo de Deploy](./README_DEPLOY_PYTHONANYWHERE.md) 