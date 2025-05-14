# Guia de Hospedagem do TechCare no PythonAnywhere

Este guia fornece instruções passo a passo para hospedar o projeto TechCare no PythonAnywhere, uma plataforma de hospedagem Python fácil de usar.

## Passo 1: Criar uma conta no PythonAnywhere

1. Acesse [PythonAnywhere](https://www.pythonanywhere.com/)
2. Clique em "Pricing & Signup" e selecione a opção gratuita "Beginner"
3. Preencha o formulário de registro e confirme seu e-mail

## Passo 2: Preparar o projeto para upload

1. Comprima todo o projeto TechCare em um arquivo ZIP
   ```
   # No Windows, você pode usar o Explorer para criar um arquivo ZIP
   # Selecione todos os arquivos da pasta techcare_python, clique com o botão direito
   # e selecione "Enviar para" > "Pasta compactada"
   ```

## Passo 3: Fazer upload e configurar o projeto

1. No PythonAnywhere, vá para a guia "Files" (Arquivos)
2. Clique em "Upload a file" (Enviar um arquivo) e faça upload do arquivo ZIP
3. Use o "Bash console" (Console Bash) para descompactar o arquivo:
   ```bash
   unzip techcare_python.zip -d techcare
   cd techcare
   ```

## Passo 4: Configurar ambiente virtual e instalar dependências

1. No console Bash, crie e ative um ambiente virtual:
   ```bash
   mkvirtualenv --python=python3.9 techcare-venv
   workon techcare-venv
   ```

2. Instale as dependências do projeto:
   ```bash
   pip install -r requirements.txt
   pip install gunicorn
   ```

## Passo 5: Configurar aplicação web

1. Vá para a guia "Web" (Web) e clique em "Add a new web app" (Adicionar nova aplicação web)
2. Escolha "Manual configuration" (Configuração manual) e selecione Python 3.9
3. Na seção "Code" (Código), configure:
   - Source code: `/home/SEU_USUARIO/techcare`
   - Working directory: `/home/SEU_USUARIO/techcare`
   - WSGI configuration file: Edite e substitua pelo código abaixo:

```python
import sys
import os

# Adicionar o diretório do projeto ao path
path = '/home/SEU_USUARIO/techcare'
if path not in sys.path:
    sys.path.append(path)

# Definir variáveis de ambiente
os.environ['FLASK_CONFIG'] = 'production'
os.environ['SECRET_KEY'] = 'sua-chave-secreta-aqui'  # Altere para uma chave segura

# Importar a aplicação
from wsgi import app as application
```

4. Na seção "Virtualenv" (Ambiente Virtual):
   - Insira o caminho `/home/SEU_USUARIO/.virtualenvs/techcare-venv`

5. Clique em "Reload" (Recarregar) para iniciar a aplicação

## Passo 6: Configurar banco de dados (opcional)

Para projetos mais avançados, você pode configurar um banco de dados MySQL:

1. Vá para a guia "Databases" (Bancos de dados)
2. Crie um novo banco de dados MySQL
3. Atualize a configuração `SQLALCHEMY_DATABASE_URI` no arquivo `config.py`

## Passo 7: Acessar a aplicação

Após a configuração, sua aplicação estará disponível no endereço:
```
http://SEU_USUARIO.pythonanywhere.com
```

Compartilhe este link com seu amigo para que ele possa acessar a aplicação.

## Solução de problemas comuns

1. **Erro 500 (Internal Server Error)**:
   - Verifique os logs de erro em "Web" > "Log files" > "Error log"
   - Certifique-se de que todas as dependências foram instaladas

2. **Arquivos estáticos não carregam**:
   - Configure a pasta de arquivos estáticos em "Web" > "Static files"
   - Adicione: URL: `/static/` Directory: `/home/SEU_USUARIO/techcare/app/static`

3. **Permissões de arquivo**:
   - Se houver erros de permissão, use `chmod` para corrigir:
   ```bash
   chmod -R 755 /home/SEU_USUARIO/techcare
   ```

## Manutenção

- Sua aplicação permanecerá online por 3 meses com a conta gratuita
- Lembre-se de acessar o painel a cada 3 meses para renovar a conta gratuita 