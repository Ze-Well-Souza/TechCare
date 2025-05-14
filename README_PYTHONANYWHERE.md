# Instruções de Deploy no PythonAnywhere

## 1. Preparação no PythonAnywhere

1. Faça login na sua conta PythonAnywhere (zewell10)
2. Abra um console Bash (clique em "Consoles" → "Bash")

## 2. Limpar ambiente atual (opcional)

Se quiser começar totalmente do zero:

```bash
# Remova instalações anteriores
rm -rf ~/mysite ~/TechCare
```

## 3. Criar diretório e extrair arquivos

```bash
# Crie um diretório limpo
mkdir -p ~/TechCare

# Extraia os arquivos (ajuste o nome do arquivo ZIP se necessário)
cd ~
unzip techcare_deploy_*.zip -d TechCare
cd TechCare

# Verifique se os arquivos foram extraídos corretamente
ls -la
```

## 4. Configurar ambiente virtual e instalar dependências

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install --upgrade pip setuptools wheel
pip install -r requirements_pythonanywhere.txt
```

## 5. Configurar o arquivo WSGI

1. Vá para a aba "Web" no dashboard do PythonAnywhere
2. Localize a seção "Code" e clique no link do seu arquivo WSGI
3. Substitua todo o conteúdo pelo conteúdo do arquivo `wsgi_pythonanywhere.py`
4. **IMPORTANTE**: Verifique se o caminho no arquivo está correto:
   - `path = '/home/Zewell10/TechCare'` (ajuste para o seu diretório)
5. Clique em "Save" para salvar as alterações

## 6. Configurar diretório da aplicação

1. Na aba "Web", localize a seção "Code"
2. Atualize "Source code" para: `/home/Zewell10/TechCare`
3. Atualize "Working directory" para: `/home/Zewell10/TechCare`
4. Verifique "WSGI configuration file"

## 7. Configurar ambiente virtual

1. Na aba "Web", localize a seção "Virtualenv"
2. Digite o caminho para seu ambiente virtual: `/home/Zewell10/TechCare/venv`
3. Clique no botão vermelho para criar/atualizar o ambiente virtual

## 8. Reiniciar a aplicação

1. Clique no botão grande verde "Reload" na parte superior da página Web
2. Verifique a aplicação acessando o URL: `zewell10.pythonanywhere.com`
