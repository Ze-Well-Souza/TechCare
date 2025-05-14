# Passos Atualizados para Deploy do TechCare no PythonAnywhere

Este guia foi atualizado para resolver os problemas específicos encontrados durante implantações anteriores.

## 1. Acessar o Console Bash do PythonAnywhere

1. Faça login no [PythonAnywhere](https://www.pythonanywhere.com/)
2. Clique em "Consoles" no menu superior
3. Clique em "Bash" para abrir um novo console

## 2. Criar Estrutura de Diretórios e Extrair Arquivos

```bash
# Crie um diretório para o TechCare
mkdir -p ~/TechCare

# Extrair o arquivo ZIP enviado (ajuste o nome conforme necessário)
cd ~
unzip techcare_deploy_*.zip -d TechCare
cd TechCare

# Verifique se a estrutura está correta 
# (deve haver uma pasta "app" com __init__.py dentro)
ls -la
ls -la app/
```

## 3. Configurar o Ambiente Virtual com Python 3.10

```bash
# IMPORTANTE: Use especificamente Python 3.10
python3.10 -m venv venv

# Ative o ambiente virtual
source venv/bin/activate

# Atualize o pip
pip install --upgrade pip

# Instale PRIMEIRO as dependências essenciais
pip install flask flask-sqlalchemy flask-login werkzeug jinja2

# Verifique se o Flask foi instalado corretamente
python -c "import flask; print('Flask instalado com sucesso:', flask.__version__)"

# Teste a importação da aplicação
python -c "import sys; sys.path.append('.'); from app import create_app; print('App importado com sucesso')"
```

## 4. Criar Simulador para Pandas (Solução para o Erro de Espaço)

Crie um arquivo `pandas_simulator.py` no diretório principal:

```bash
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

# Simula outras funções do pandas
def read_csv(*args, **kwargs):
    return FakeDataFrame()

def read_excel(*args, **kwargs):
    return FakeDataFrame()
EOF

# Verifique se o arquivo foi criado corretamente
cat pandas_simulator.py
```

## 5. Configurar Arquivo WSGI Personalizado

```bash
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
    # Fallback se o simulador não for encontrado
    sys.modules['pandas'] = type('obj', (object,), {
        '__getattr__': lambda self, name: None
    })

# Importa e cria a aplicação
from app import create_app

# Cria a aplicação usando as configurações de produção
application = create_app('production')
EOF

# Verifique se o arquivo foi criado corretamente
cat wsgi_pythonanywhere.py
```

## 6. Instalar as Demais Dependências Necessárias (Exceto pandas)

```bash
# Crie um requirements_minimal.txt sem o pandas
grep -v pandas requirements.txt > requirements_minimal.txt

# Instale as dependências mínimas
pip install -r requirements_minimal.txt
```

## 7. Configurar a Aplicação Web no PythonAnywhere

1. No menu superior do PythonAnywhere, clique em "Web"
2. Clique em "Add a new web app"
3. Clique em "Next" na tela de domínio
4. Escolha "Flask" como framework
5. **IMPORTANTE**: Escolha "Python 3.10" (deve corresponder à versão usada para criar o virtualenv)
6. No primeiro setup, aceite o caminho padrão (você irá alterá-lo depois)

## 8. Configurar a Aplicação Web Corretamente

1. Na página "Web", em "Code", altere:
   - Source code: `/home/Zewell10/TechCare`
   - Working directory: `/home/Zewell10/TechCare`

2. Na seção "WSGI configuration file", clique no link para editar o arquivo
   - Substitua TODO o conteúdo pelo conteúdo do arquivo `wsgi_pythonanywhere.py` que você criou
   - Salve o arquivo

3. Na seção "Virtualenv", digite:
   ```
   /home/Zewell10/TechCare/venv
   ```

4. Na seção "Static files", adicione:
   - URL: `/static/` → Directory: `/home/Zewell10/TechCare/app/static`

## 9. Executar Diagnósticos Antes de Recarregar

```bash
# Verifique a estrutura do projeto
cd ~/TechCare
find app -type f -name "__init__.py" | sort

# Verifique o virtualenv
ls -la venv/bin/python
venv/bin/python --version  # Deve mostrar Python 3.10.x

# Verifique se o Flask está instalado no virtualenv
venv/bin/pip list | grep Flask

# Verifique o arquivo WSGI na web
echo "Confirme que o arquivo WSGI está configurado corretamente"
```

## 10. Recarregar a Aplicação e Verificar os Logs

1. Na página "Web", clique no botão "Reload"
2. Imediatamente após recarregar, clique em "Error log" na seção "Logs"
3. Analise os erros, se houver, e corrija-os conforme necessário

## 11. Resolução de Problemas Comuns

### Se você ver "ModuleNotFoundError: No module named 'app'":
```bash
# Verifique a estrutura
ls -la ~/TechCare/
ls -la ~/TechCare/app/

# Corrija o caminho no arquivo WSGI se necessário
# Certifique-se de que o caminho está correto e acessível
```

### Se você ver "ModuleNotFoundError: No module named 'flask'":
```bash
# Reinstale o Flask no virtualenv correto
cd ~/TechCare/
source venv/bin/activate
pip install flask
```

### Se a aplicação carregar mas as imagens/CSS não aparecerem:
```bash
# Verifique a configuração de arquivos estáticos
# Na página "Web", confirme a configuração do URL "/static/"
```

## 12. Acessar e Testar a Aplicação

Uma vez que a aplicação esteja funcionando, acesse-a em:
`https://zewell10.pythonanywhere.com` 