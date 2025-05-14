# Guia de Execução - TechCare

Este documento contém instruções detalhadas para executar o projeto TechCare em diferentes ambientes. Siga as orientações abaixo para configurar e executar a aplicação corretamente.

## Execução Local

### Pré-requisitos

- Python 3.8 ou superior
- Sistema operacional: Windows, Linux ou macOS
- Acesso administrativo à máquina (para análise completa do sistema)

### Configuração do Ambiente

1. **Prepare o ambiente virtual:**

   ```
   python setup_local_env.py
   ```

   Este script irá:
   - Criar um ambiente virtual na pasta `venv`
   - Instalar todas as dependências necessárias
   - Adaptar a instalação conforme o seu sistema operacional

2. **Ative o ambiente virtual:**

   - Windows:
     ```
     venv\Scripts\activate
     ```

   - Linux/macOS:
     ```
     source venv/bin/activate
     ```

### Execução da Aplicação

Para iniciar a aplicação em modo de desenvolvimento:

```
python run_local.py --debug
```

Parâmetros disponíveis:

- `--host`: Define o host para executar o servidor (padrão: 127.0.0.1)
- `--port`: Define a porta para executar o servidor (padrão: 5000)
- `--debug`: Ativa o modo de depuração
- `--env`: Define o ambiente (development, testing, production)

Exemplo de uso:

```
python run_local.py --host 0.0.0.0 --port 8080 --env production
```

## Execução no PythonAnywhere

### Configuração Inicial

1. Crie uma conta no PythonAnywhere (ou use sua conta existente)
2. Faça upload do pacote de deploy:
   - Use `create_deploy_package.py` para criar o pacote:
     ```
     python create_deploy_package.py
     ```
   - Faça upload do arquivo zip gerado para o PythonAnywhere

3. Descompacte o arquivo no PythonAnywhere:
   ```
   unzip techcare_deploy_package.zip
   ```

4. Configure o ambiente no PythonAnywhere:
   ```
   python fix_pandas_pythonanywhere.py
   ```

### Configuração da Aplicação Web

1. No painel do PythonAnywhere, vá para a seção "Web"
2. Clique em "Add a new web app"
3. Escolha "Manual configuration" e selecione Python 3.8
4. Configure o caminho para o arquivo WSGI:
   - Edite o arquivo WSGI gerado pelo PythonAnywhere
   - Substitua o conteúdo pelo seguinte:

   ```python
   import sys
   import os

   path = '/home/SEUNOME/techcare'  # Substitua SEUNOME pelo seu nome de usuário no PythonAnywhere
   if path not in sys.path:
       sys.path.append(path)

   os.environ['FLASK_ENV'] = 'production'
   os.environ['FLASK_CONFIG'] = 'production'

   from app import create_app
   application = create_app('production')
   ```

5. Configure os arquivos estáticos:
   - URL: /static/
   - Diretório: /home/SEUNOME/techcare/app/static

6. Reinicie a aplicação pelo painel do PythonAnywhere

## Solução de Problemas Comuns

### Problemas de Dependências

- **Erro no Windows com pacotes pywin32 ou wmi**:
  Os pacotes Windows são instalados apenas em sistemas Windows. Em outros sistemas, eles são ignorados automaticamente pelo script `setup_local_env.py`.

- **Erro com pandas no PythonAnywhere**:
  Execute `fix_pandas_pythonanywhere.py` para instalar uma versão compatível do pandas.

### Problemas de Acesso a Arquivos

- **Erro de permissão ao acessar diretórios**:
  Certifique-se de que o usuário que está executando a aplicação tem permissão para escrever nos diretórios de dados:
  - instance/diagnostics
  - instance/repair_logs
  - instance/diagnostics_storage

### Problemas de Banco de Dados

- **Erro ao conectar ao banco de dados**:
  Por padrão, a aplicação usa SQLite. Verifique se o diretório `instance` existe e se o aplicativo tem permissão para escrever nele.

## Comandos para Testes

Para executar os testes automatizados:

```
python run_tests.py
```

Ou para testes específicos:

```
pytest tests/test_diagnostic.py -v
```

---

Se encontrar qualquer problema não listado aqui, consulte a documentação oficial ou entre em contato com o suporte técnico. 