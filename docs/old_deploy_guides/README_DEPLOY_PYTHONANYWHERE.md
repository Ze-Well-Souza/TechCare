# Guia de Implantação no PythonAnywhere

Este documento contém instruções passo a passo para implantar o TechCare em uma conta gratuita do PythonAnywhere.

## Pré-requisitos

- Uma conta PythonAnywhere (você pode criar uma gratuita em [pythonanywhere.com](https://www.pythonanywhere.com))
- Os arquivos do projeto TechCare

## Considerações Importantes para o Deploy

### Limitações da Conta Gratuita PythonAnywhere
- Espaço em disco limitado (aprox. 512MB)
- Bibliotecas grandes como pandas podem causar problemas de instalação
- Algumas bibliotecas Windows não são compatíveis (pywin32, wmi)

### Soluções para Problemas Comuns
- **Uso do pandas**: Será substituído por simulação na produção para evitar problemas de espaço
- **Bibliotecas Windows**: Serão tratadas com verificações condicionais
- **Caminhos absolutos**: Serão ajustados para funcionar no ambiente Linux

## Método 1: Deploy Manual Otimizado (Recomendado)

Este método foi revisado para evitar os problemas específicos encontrados em tentativas anteriores.

### Etapa 1: Extrair os arquivos no PythonAnywhere

```bash
# Acesse o console Bash do PythonAnywhere
# Crie um diretório para o projeto (se ainda não existir)
mkdir -p ~/TechCare

# Faça upload do arquivo ZIP pelo painel do PythonAnywhere
# OU use o comando abaixo se for via URL
# wget URL_DO_ARQUIVO -O ~/techcare_deploy.zip

# Extraia o arquivo (ajuste o nome do arquivo se necessário)
cd ~
unzip techcare_deploy_*.zip -d TechCare
```

### Etapa 2: Preparar o ambiente virtual com a versão correta do Python

```bash
# Acesse o diretório do projeto
cd ~/TechCare

# Crie o ambiente virtual com Python 3.10 específico
python3.10 -m venv venv

# Ative o ambiente virtual
source venv/bin/activate

# Atualize o pip
pip install --upgrade pip

# Instale primeiro as dependências essenciais
pip install flask flask-sqlalchemy flask-login werkzeug jinja2

# Em seguida, instale as demais dependências exceto pandas
# (criamos um arquivo requirements_minimal.txt sem pandas)
pip install -r requirements_minimal.txt
```

### Etapa 3: Configurar o arquivo WSGI personalizado

Crie um arquivo `wsgi_pythonanywhere.py` no diretório do projeto com o seguinte conteúdo:

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

# Trata bibliotecas problemáticas - simula pandas
sys.modules['pandas'] = type('obj', (object,), {
    '__getattr__': lambda self, name: None
})

# Importa e cria a aplicação
from app import create_app

# Cria a aplicação usando as configurações de produção
application = create_app('production')
```

### Etapa 4: Configurar a aplicação web no PythonAnywhere

1. No PythonAnywhere, acesse a guia "Web"
2. Clique em "Add a new web app"
3. Selecione "Flask" e Python 3.10
4. **IMPORTANTE**: Configure corretamente os caminhos:
   - Source code: `/home/Zewell10/TechCare`
   - Working directory: `/home/Zewell10/TechCare`
   - WSGI configuration file: Substitua o conteúdo pelo arquivo `wsgi_pythonanywhere.py` criado acima
5. Configure o virtualenv: `/home/Zewell10/TechCare/venv`
6. Para arquivos estáticos: URL `/static/` → Directory `/home/Zewell10/TechCare/app/static`

### Etapa 5: Verificar logs e resolver problemas

Após clicar em "Reload", verifique imediatamente os logs de erro:

1. Na página "Web", role até a seção "Logs"
2. Clique em "Error log" para verificar possíveis erros

#### Problemas comuns e suas soluções:

**"No module named 'app'"**
- Verifique se o caminho no arquivo WSGI está correto
- Confirme que existe uma pasta "app" no diretório `/home/Zewell10/TechCare`
- Verifique se a estrutura da pasta app está correta (deve ter um `__init__.py`)

**"No module named 'flask'"**
- Verifique se o virtualenv está ativado e configurado corretamente
- Reinstale o Flask: `pip install flask`
- Confirme se o caminho do virtualenv no painel web está correto

**"Disk quota exceeded"**
- Limpe arquivos temporários ou desnecessários
- Use um requirements.txt mínimo, sem dependências grandes como pandas
- Considere fazer upgrade para uma conta paga se precisar de todas as dependências

## Método 2: Deploy com Simulação de Dependências Pesadas

Este método é ideal para quem enfrenta problemas com o limite de espaço da conta gratuita.

### Etapa 1: Criar um módulo de simulação para pandas

Crie um arquivo `pandas_simulator.py` no diretório raiz do projeto:

```python
"""
Módulo simulador para substituir pandas em produção.
Reduz o uso de espaço em disco no PythonAnywhere.
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

# Outros métodos e classes simulados conforme necessário
```

### Etapa 2: Modificar o arquivo WSGI para usar a simulação

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

# Simula pandas usando nosso módulo personalizado
sys.path.insert(0, '/home/Zewell10/TechCare')
import pandas_simulator
sys.modules['pandas'] = pandas_simulator

# Importa e cria a aplicação
from app import create_app

# Cria a aplicação usando as configurações de produção
application = create_app('production')
```

## Checklist Final de Verificação

Antes de considerar o deploy finalizado, verifique:

1. A aplicação está respondendo no URL correto
2. Os logs de erro estão limpos
3. Todas as funcionalidades essenciais funcionam corretamente
4. Os arquivos estáticos (CSS, JS, imagens) estão sendo carregados

## Manutenção e Atualizações

Para atualizações futuras:

1. Faça backup dos arquivos de configuração personalizados
2. Extraia os novos arquivos, preservando as configurações
3. Se necessário, atualize o ambiente virtual
4. Clique em "Reload" para aplicar as mudanças

## Suporte e Recursos Adicionais

- [Debugging Import Errors no PythonAnywhere](https://help.pythonanywhere.com/pages/DebuggingImportError/)
- [Limites de conta gratuita](https://help.pythonanywhere.com/pages/FreeAccount/)
- [Fórum do PythonAnywhere](https://www.pythonanywhere.com/forums/) 