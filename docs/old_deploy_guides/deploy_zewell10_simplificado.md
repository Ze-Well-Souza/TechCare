# Deploy Simplificado do TechCare no PythonAnywhere

Este guia reinicia todo o processo de deploy do zero, com passos simplificados e diretos.

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

# Ativar ambiente virtual (agora este comando funcionará)
source venv/bin/activate

# Instalar dependências básicas
pip install setuptools wheel

# Instalar dependências mínimas necessárias
pip install flask==3.1.0 flask-login==0.6.3 flask-wtf==1.2.1 sqlalchemy==2.0.32 requests==2.31.0 psutil==7.0.0 py-cpuinfo==9.0.0
```