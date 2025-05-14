# Guia Detalhado de Deploy no PythonAnywhere

Este guia contém instruções passo a passo para hospedar o sistema TechCare no PythonAnywhere.

## Preparação Inicial

### 1. Criar uma Conta no PythonAnywhere
1. Acesse [PythonAnywhere](https://www.pythonanywhere.com/)
2. Clique em "Pricing & Signup" e selecione a opção gratuita "Beginner"
3. Preencha o formulário de registro e confirme seu e-mail

### 2. Preparar o Código para Upload
1. Certifique-se de que todos os testes estão passando: `python run_tests.py`
2. Comprima os arquivos do projeto (exceto pastas `venv`, `__pycache__`, `.pytest_cache` e `.git`)
3. Recomendamos incluir no ZIP:
   - Todos os diretórios: `app`, `config`, `data`, `scripts`
   - Arquivos: `requirements_pythonanywhere.txt`, `wsgi.py`, `config.py`
   - Documentação: `README.md`, `TASK_MASTER.md`

## Upload e Configuração

### 3. Fazer Upload do Projeto
1. Faça login no PythonAnywhere
2. Na aba "Files", clique em "Upload a file" e selecione o arquivo ZIP do projeto
3. Abra um console Bash através da guia "Consoles"
4. Descompacte o arquivo:
   ```bash
   unzip nome_do_arquivo.zip -d techcare
   cd techcare
   ```

### 4. Configurar Ambiente Virtual e Instalar Dependências
1. No console Bash, crie um ambiente virtual:
   ```bash
   mkvirtualenv --python=python3.9 techcare-venv
   ```
2. Ative o ambiente virtual:
   ```bash
   workon techcare-venv
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements_pythonanywhere.txt
   ```

### 5. Criar e Configurar Web App
1. Vá para a aba "Web"
2. Clique em "Add a new web app"
3. Escolha o seu domínio (será algo como seu_usuario.pythonanywhere.com)
4. Selecione "Manual configuration"
5. Escolha Python 3.9

### 6. Configurar os Arquivos de Código e Ambiente Virtual
1. Em "Code" na aba "Web", configure:
   - Source code: `/home/seu_usuario/techcare`
   - Working directory: `/home/seu_usuario/techcare`
2. Em "Virtualenv", configure:
   - Caminho: `/home/seu_usuario/.virtualenvs/techcare-venv`

### 7. Configurar o Arquivo WSGI
1. Clique no link para editar o arquivo WSGI
2. Substitua todo o conteúdo pelo código abaixo (ajustando o caminho):
   ```python
   import sys
   import os
   
   # Adiciona o diretório do projeto ao path do Python
   path = '/home/seu_usuario/techcare'
   if path not in sys.path:
       sys.path.append(path)
   
   # Definir variáveis de ambiente para produção
   os.environ['FLASK_CONFIG'] = 'production'
   os.environ['SECRET_KEY'] = 'ef8b22d09137082c194992cc8c3097e0d93422ba83a61a2993ec3169fcee3564'
   
   # Cria pastas de dados necessárias
   data_path = os.path.join(path, 'data')
   diagnostic_path = os.path.join(data_path, 'diagnostics')
   repair_path = os.path.join(data_path, 'repair_logs')
   diagnostic_storage = os.path.join(data_path, 'diagnostics_storage')
   
   os.makedirs(data_path, exist_ok=True)
   os.makedirs(diagnostic_path, exist_ok=True)
   os.makedirs(repair_path, exist_ok=True)
   os.makedirs(diagnostic_storage, exist_ok=True)
   
   # Importa a aplicação Flask
   from wsgi import app as application
   ```

### 8. Configurar Arquivos Estáticos
1. Na seção "Static files" da aba "Web":
2. Adicione um novo mapeamento:
   - URL: `/static`
   - Directory: `/home/seu_usuario/techcare/app/static`

### 9. Inicializar o Banco de Dados (Se Necessário)
1. Abra um novo console Bash
2. Ative o ambiente virtual:
   ```bash
   workon techcare-venv
   ```
3. Navegue até o diretório do projeto:
   ```bash
   cd /home/seu_usuario/techcare
   ```
4. Execute o script de inicialização do banco de dados (se existir):
   ```bash
   python scripts/init_db.py
   ```
   Ou crie um script simples para inicializar o banco:
   ```python
   from app import create_app, db
   app = create_app('production')
   with app.app_context():
       db.create_all()
   ```

### 10. Finalizar e Iniciar o App
1. Verifique se todas as configurações estão corretas
2. Clique no botão verde "Reload" para iniciar a aplicação
3. Acesse seu site em `https://seu_usuario.pythonanywhere.com`

## Solução de Problemas

### Arquivos Estáticos Não Carregam
- Verifique se o mapeamento de arquivos estáticos está correto
- Confirme que os arquivos existem no caminho especificado

### Erros de Importação
- Verifique se o caminho do projeto no arquivo WSGI está correto
- Certifique-se de que todas as dependências foram instaladas

### Erros de Banco de Dados
- Verifique se o banco de dados foi criado corretamente
- Confirme as permissões nos diretórios de dados

### Logs de Erro
- Na aba "Web", verifique os logs de erro e acesso
- Os logs podem fornecer informações sobre o que está causando o problema

## Manutenção

### Atualizar o Código
1. Faça upload do novo código
2. Se necessário, atualize as dependências:
   ```bash
   workon techcare-venv
   pip install -r requirements_pythonanywhere.txt
   ```
3. Clique em "Reload" para reiniciar a aplicação

### Backup do Banco de Dados
1. Na aba "Files", navegue até o diretório dos dados
2. Selecione o arquivo do banco de dados e clique em "Download"
3. Para maior segurança, configure backups automáticos (planos pagos)

### Monitoramento
- Verifique regularmente os logs de erro
- Configure um script para verificar a disponibilidade do site

## Considerações Finais

- A conta gratuita do PythonAnywhere desativa aplicações que não são acessadas por 3 meses
- Para aplicações de produção, considere um plano pago
- Para maior confiabilidade, considere migrar para PostgreSQL (planos pagos)
- Para maior segurança, certifique-se de que a SECRET_KEY seja mantida confidencial

Boa sorte com o deploy! Se precisar de ajuda adicional, consulte a [documentação oficial do PythonAnywhere](https://help.pythonanywhere.com/). 