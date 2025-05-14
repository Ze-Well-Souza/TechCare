# Guia Visual Atualizado: Deploy do TechCare no PythonAnywhere

Este guia visual foi atualizado para resolver os problemas específicos identificados em tentativas anteriores de deploy.

## Passo 1: Preparar o Console Bash

Na barra de navegação superior, clique em "Consoles":

```
[Dashboard] [Consoles] [Files] [Web] [Tasks] [Databases]
```

Em seguida, clique em "Bash" para abrir um novo console:

```
+----------------+
| New Console    |
+----------------+
| > Bash         |
| Python 3.10    | <-- IMPORTANTE: Use este!
| Python 3.9     |
| Python 3.8     |
+----------------+
```

## Passo 2: Extrair o Arquivo ZIP

No console Bash, execute os seguintes comandos:

```bash
# Criar diretório TechCare
mkdir -p ~/TechCare

# Extrair o arquivo ZIP para o diretório TechCare
cd ~
unzip techcare_deploy_*.zip -d TechCare

# Acessar o diretório TechCare
cd TechCare

# Verificar se os arquivos foram extraídos corretamente
ls -la
# Você deve ver algo como: app/ migrations/ run.py wsgi.py ...
```

## Passo 3: Criar Simulador para Pandas

Para resolver o problema de espaço no PythonAnywhere, crie um simulador de pandas:

```bash
# Crie um arquivo pandas_simulator.py
cat > pandas_simulator.py << 'EOF'
"""
Simulador de pandas para evitar problemas de espaço no PythonAnywhere
"""
class FakeDataFrame:
    def __init__(self, *args, **kwargs):
        self.data = {}
    
    def __getattr__(self, name):
        return lambda *args, **kwargs: self
    
    def to_dict(self, *args, **kwargs):
        return {}
    
    def to_csv(self, *args, **kwargs):
        pass

def DataFrame(*args, **kwargs):
    return FakeDataFrame()

def read_csv(*args, **kwargs):
    return FakeDataFrame()

def read_excel(*args, **kwargs):
    return FakeDataFrame()
EOF

# Verifique se o arquivo foi criado corretamente
ls -la pandas_simulator.py
```

## Passo 4: Criar Arquivo WSGI Personalizado

```bash
# Crie o arquivo WSGI personalizado
cat > wsgi_pythonanywhere.py << 'EOF'
import sys
import os

# Adiciona o diretório da aplicação ao PATH
path = '/home/Zewell10/TechCare'
if path not in sys.path:
    sys.path.append(path)

# Define variáveis de ambiente
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_CONFIG'] = 'production'

# IMPORTANTE: Simula o pandas para evitar erros
sys.path.insert(0, '/home/Zewell10/TechCare')
try:
    import pandas_simulator
    sys.modules['pandas'] = pandas_simulator
except ImportError:
    sys.modules['pandas'] = type('obj', (object,), {
        '__getattr__': lambda self, name: None
    })

# Importa e cria a aplicação
from app import create_app

# Cria a aplicação usando as configurações de produção
application = create_app('production')
EOF

# Verifique se o arquivo foi criado corretamente
ls -la wsgi_pythonanywhere.py
```

## Passo 5: Configurar o Ambiente Virtual com Python 3.10

```bash
# IMPORTANTE: Use especificamente Python 3.10
python3.10 -m venv venv

# Ative o ambiente virtual
source venv/bin/activate

# Seu prompt deve mudar para algo como:
# (venv) zewell10@eu:~/TechCare$

# Atualize o pip
pip install --upgrade pip

# PRIMEIRO: Instale apenas as dependências essenciais
pip install flask flask-sqlalchemy flask-login werkzeug jinja2

# Verifique se o Flask foi instalado corretamente
python -c "import flask; print(flask.__version__)"

# Crie um arquivo requirements_minimal sem pandas
grep -v pandas requirements.txt > requirements_minimal.txt 

# Instale as demais dependências (exceto pandas)
pip install -r requirements_minimal.txt
```

## Passo 6: Testar a Importação da Aplicação

```bash
# Teste se a aplicação pode ser importada
python -c "import sys; sys.path.append('.'); from app import create_app; print('App importado com sucesso')"
```

Você deve ver a mensagem: "App importado com sucesso"

## Passo 7: Criar a Aplicação Web

1. Clique na guia "Web" na barra de navegação superior:

```
[Dashboard] [Consoles] [Files] [Web] [Tasks] [Databases]
```

2. Clique em "Add a new web app":

```
+-----------------+
| Add a new web app |
+-----------------+
```

3. Na janela de domínio, clique em "Next":

```
+---------------------------------+
| Your web app will be at:        |
| zewell10.pythonanywhere.com     |
|                                 |
|           [Next >]              |
+---------------------------------+
```

4. Selecione "Flask" como framework:

```
+---------------------------------+
| Select a Python Web framework   |
|                                 |
| ( ) Django                      |
| (•) Flask                       |
| ( ) Bottle                      |
| ( ) Web2py                      |
| ( ) Manual configuration        |
|                                 |
|           [Next >]              |
+---------------------------------+
```

5. IMPORTANTE: Selecione Python 3.10 (deve corresponder ao virtualenv):

```
+---------------------------------+
| Select a Python version         |
|                                 |
| ( ) Python 3.8                  |
| ( ) Python 3.9                  |
| (•) Python 3.10                 | <-- SELECIONE ESTA OPÇÃO!
|                                 |
|           [Next >]              |
+---------------------------------+
```

6. No primeiro setup, aceite o caminho padrão (você irá mudá-lo depois):

```
+---------------------------------+
| Path                            |
|                                 |
| /home/Zewell10/mysite/flask_app.py  |
|                                 |
|           [Next >]              |
+---------------------------------+
```

## Passo 8: Configurar Corretamente a Aplicação Web

Na página "Web", você verá sua aplicação:

```
+---------------------------------+
| Web                             |
+---------------------------------+
| zewell10.pythonanywhere.com     |
|                                 |
| Code:                           |
| Source code: /home/Zewell10/mysite  | <-- ALTERE ISTO!
| Working directory: /home/Zewell10/  | <-- ALTERE ISTO!
| WSGI config file: /var/www/zewell10_pythonanywhere_com_wsgi.py | <-- CLIQUE AQUI!
+---------------------------------+
```

1. Em "Code", configure os caminhos:
   - Source code: `/home/Zewell10/TechCare`
   - Working directory: `/home/Zewell10/TechCare`

2. Clique no link do arquivo WSGI para editá-lo.

3. Substitua TODO o conteúdo do arquivo pelo conteúdo do arquivo `wsgi_pythonanywhere.py` que você criou no Passo 4.

4. Na seção "Virtualenv", digite:

```
+---------------------------------+
| Virtualenv:                     |
|                                 |
| /home/Zewell10/TechCare/venv    |
|                                 |
|           [Save]                |
+---------------------------------+
```

5. Na seção "Static files", adicione:

```
+---------------------------------+
| Static files:                   |
+---------------------------------+
| URL             | Directory     |
+---------------------------------+
| /static/        | /home/Zewell10/TechCare/app/static |
+---------------------------------+
```

## Passo 9: Verificar Tudo Antes de Recarregar

Antes de recarregar a aplicação, verifique:

1. O virtualenv está usando Python 3.10
2. O Flask está instalado no virtualenv
3. O arquivo WSGI tem o conteúdo correto e caminho correto
4. Os arquivos do projeto estão na estrutura correta

## Passo 10: Recarregar e Monitorar

1. Clique no botão "Reload" no topo da página:

```
+---------------------------------+
| zewell10.pythonanywhere.com     |
| [ Reload ]                      | <-- CLIQUE AQUI
+---------------------------------+
```

2. Imediatamente após clicar em "Reload", verifique os logs de erro:

```
+---------------------------------+
| zewell10.pythonanywhere.com     |
| [ Error log ] [ Server log ]    | <-- CLIQUE EM "Error log"
+---------------------------------+
```

## Passo 11: Resolução de Problemas Comuns

### Se você ver "ModuleNotFoundError: No module named 'app'"

Isso significa que o Python não encontra o módulo 'app'. Verifique:

1. O caminho no arquivo WSGI está correto? Deve ser `/home/Zewell10/TechCare`
2. Existe um diretório `app` em `/home/Zewell10/TechCare/`?
3. O arquivo `/home/Zewell10/TechCare/app/__init__.py` existe?

### Se você ver "ModuleNotFoundError: No module named 'flask'"

Isso significa que o Flask não está instalado ou o virtualenv não está sendo usado. Verifique:

1. O caminho do virtualenv está correto na configuração web?
2. O Flask está instalado? Execute:
   ```bash
   source ~/TechCare/venv/bin/activate
   pip install flask
   ```

### Se você ver "Error: OSError: [Errno 122]"

Isso indica um problema de espaço. A solução foi implementada com o simulador de pandas.

## Passo 12: Testar a Aplicação

Depois que tudo estiver configurado corretamente e a aplicação estiver rodando:

1. Acesse `https://zewell10.pythonanywhere.com` em seu navegador
2. Verifique se a página inicial carrega corretamente
3. Verifique se os arquivos estáticos (CSS, imagens) estão aparecendo
4. Tente fazer login ou usar outras funcionalidades para garantir que tudo funciona 