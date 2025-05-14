# Configuração do Ambiente Virtual no PythonAnywhere

Este guia foi atualizado para resolver os problemas específicos encontrados durante o deploy no PythonAnywhere.

## 1. Criação do Ambiente Virtual com a Versão Correta do Python

É fundamental utilizar a versão do Python que está configurada no painel do PythonAnywhere (Python 3.10).

```bash
# Acesse o diretório do projeto
cd /home/Zewell10/TechCare

# Se já existir um virtualenv com a versão errada, remova-o
rm -rf venv

# Crie um novo virtualenv usando Python 3.10
python3.10 -m venv venv

# Ative o ambiente virtual
source venv/bin/activate

# Atualize o pip
pip install --upgrade pip

# IMPORTANTE: Instale as dependências essenciais PRIMEIRO
pip install flask flask-sqlalchemy flask-login werkzeug jinja2

# Verifique se o Flask foi instalado corretamente
python -c "import flask; print(flask.__version__)"
```

## 2. Instalação Estratégica de Dependências

Para evitar problemas de espaço em disco (erro "OSError: [Errno 122]"), siga esta abordagem escalonada:

```bash
# Primeiro, instale apenas as dependências críticas para inicialização
pip install -r requirements_minimal.txt

# Se houver espaço, tente instalar as demais dependências
# EVITE instalar pandas - ele é muito grande e causa problemas de espaço
pip install matplotlib
pip install pdfkit
# ... e outras dependências menores
```

## 3. Configuração do Virtualenv no Painel Web

Configure o caminho do ambiente virtual na interface do PythonAnywhere:

1. Na página "Web", localize a seção "Virtualenv"
2. Clique em "Enter path to a virtualenv, if desired"
3. Digite o caminho completo para o ambiente virtual:
   ```
   /home/Zewell10/TechCare/venv
   ```
4. Clique em "Save"
5. **NÃO CLIQUE EM RELOAD AINDA!** - Primeiro configure o arquivo WSGI

## 4. Configuração do WSGI com Tratamento Especial para Pandas

Crie um arquivo chamado `wsgi_pythonanywhere.py` no diretório do projeto:

```python
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
# Isso cria um "pandas falso" que não causa erros ao ser importado
sys.modules['pandas'] = type('obj', (object,), {
    '__getattr__': lambda self, name: None
})

# Importa e cria a aplicação
from app import create_app

# Cria a aplicação usando as configurações de produção
application = create_app('production')
```

## 5. Configuração do Arquivo WSGI no PythonAnywhere

No arquivo WSGI do PythonAnywhere (`/var/www/Zewell10_pythonanywhere_com_wsgi.py`):

1. Acesse a guia "Web" do PythonAnywhere
2. Localize a seção "Code" e clique no link "WSGI configuration file"
3. Substitua TODO o conteúdo pelo contido no arquivo `wsgi_pythonanywhere.py` que criamos
4. Salve o arquivo

## 6. Verificação do Funcionamento do Flask

Antes de recarregar a aplicação, verifique se o Flask está funcionando:

```bash
# No console do PythonAnywhere
cd /home/Zewell10/TechCare
source venv/bin/activate

# Teste a importação do Flask
python -c "import flask; print('Flask instalado: ' + flask.__version__)"

# Teste a importação da sua aplicação
python -c "from app import create_app; print('App importado com sucesso')"
```

Se esses comandos funcionarem sem erros, o problema de importação foi resolvido.

## 7. Recarregue a Aplicação

Agora você pode clicar em "Reload" na página Web do PythonAnywhere.

## 8. Solução de Problemas Específicos

### Problema: "ModuleNotFoundError: No module named 'app'"
- Causa: O Python não consegue encontrar o módulo 'app'
- Solução: 
  1. Verifique se a estrutura de diretórios está correta
  2. Confirme que existe uma pasta `app` em `/home/Zewell10/TechCare/`
  3. Verifique se o caminho no arquivo WSGI está correto

### Problema: "ModuleNotFoundError: No module named 'flask'"
- Causa: Flask não está instalado no virtualenv ou o virtualenv não está sendo usado
- Solução:
  1. Reinstale o Flask: `pip install flask`
  2. Verifique o caminho do virtualenv no painel do PythonAnywhere
  3. Certifique-se de que o ambiente virtual está ativado ao instalar o Flask

### Problema: "Error: OSError: [Errno 122]"
- Causa: Espaço em disco excedido (limitação da conta gratuita)
- Solução:
  1. Use a abordagem de simulação de pandas
  2. Instale apenas as dependências essenciais
  3. Limpe arquivos temporários, logs ou outras coisas que ocupem espaço

## 9. Comandos Úteis

### Para verificar o espaço em disco disponível
```bash
du -sh ~
```

### Para limpar arquivos temporários e PYC
```bash
find ~/TechCare -name "*.pyc" -delete
find ~/TechCare -name "__pycache__" -type d -exec rm -rf {} +
```

### Para verificar a versão do Python no virtualenv
```bash
/home/Zewell10/TechCare/venv/bin/python --version
``` 