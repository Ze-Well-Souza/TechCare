# Como resolver o problema de instalação do pandas no PythonAnywhere

Vejo que você está enfrentando um erro durante a instalação das dependências, especificamente relacionado ao pacote `pandas`. Esse é um problema comum no PythonAnywhere, pois o pandas 2.1.4 requer compilação de código nativo, o que pode falhar no ambiente deles.

## Solução 1: Usar uma versão mais antiga do pandas (Recomendada)

1. Crie um novo arquivo requirements ajustado:

```bash
# No console do PythonAnywhere
cd ~/TechCare
cat > requirements_fixed.txt << EOF
flask==3.1.0
pytest==8.3.5
psutil==7.0.0
py-cpuinfo==9.0.0
sqlalchemy==2.0.32
flask-login==0.6.3
flask-wtf==1.2.1
pytest-cov==4.1.0
requests==2.31.0
pathlib==1.0.1
plotly==5.18.0
pandas==1.5.3
EOF
```

2. Desative o ambiente virtual atual e crie um novo:

```bash
deactivate
rm -rf ~/TechCare/venv
python3 -m venv ~/TechCare/venv
source ~/TechCare/venv/bin/activate
```

3. Instale as dependências ajustadas:

```bash
pip install -r requirements_fixed.txt
```

## Solução 2: Instalar apenas os pacotes essenciais

Se a Solução 1 não funcionar, podemos instalar apenas os pacotes essenciais para a aplicação:

```bash
pip install flask==3.1.0 flask-login==0.6.3 flask-wtf==1.2.1 sqlalchemy==2.0.32 requests==2.31.0
```

## Solução 3: Usar wheel pré-compilado para pandas

Se você realmente precisar do pandas:

```bash
pip install --only-binary=pandas pandas==1.5.3
```

## Finalizar a instalação

Depois de resolver o problema do pandas, continue com os passos de configuração da aplicação web:

1. No menu do PythonAnywhere, acesse "Web"
2. Clique em "Add a new web app"
3. Selecione "Flask" como framework
4. Escolha a versão mais recente do Python
5. Configure os caminhos conforme instruído anteriormente
6. Configure o arquivo WSGI
7. Defina o caminho do virtualenv para `/home/zewell10/TechCare/venv`
8. Configure os arquivos estáticos
9. Clique em "Reload" para iniciar a aplicação

## Verificar se a aplicação está funcionando

Acesse https://zewell10.pythonanywhere.com para verificar se a aplicação está funcionando corretamente. 