# Guia de Deploy do TechCare no PythonAnywhere

## Introdução

Este guia contém instruções atualizadas e completas para fazer o deploy do TechCare no PythonAnywhere, considerando as limitações da plataforma e as melhores práticas.

## Pré-requisitos

- Uma conta no PythonAnywhere (gratuita ou paga) - [Criar conta](https://www.pythonanywhere.com/)
- Token de API (acessível em Account > API Token)
- Acesso aos arquivos do projeto TechCare

## Limitações conhecidas e soluções

### Problema com o pandas

O PythonAnywhere tem limitações de memória que impedem a instalação de versões recentes do pandas (2.x). Para contornar esse problema, criamos:

1. Um arquivo `requirements_pythonanywhere_updated.txt` com a versão 1.5.3 do pandas
2. Um script `fix_pandas_pythonanywhere.py` que instala as dependências corretas

Estes arquivos são utilizados automaticamente pelo script de upload.

## Métodos de Deploy

Existem duas formas de fazer o deploy no PythonAnywhere:

### 1. Deploy Automatizado (Recomendado)

Esta é a forma mais rápida e menos sujeita a erros.

1. **Verificar prontidão para deploy**:
   ```bash
   python setup_local_env.py
   python run_local.py --debug
   ```
   Certifique-se de que a aplicação está funcionando localmente antes de prosseguir.

2. **Executar o script de upload**:
   ```bash
   python upload_to_pythonanywhere.py --username SEU_USUARIO --token SEU_TOKEN_API
   ```
   Substitua `SEU_USUARIO` e `SEU_TOKEN_API` pelos seus dados do PythonAnywhere.

3. **Configurar a aplicação web** no painel do PythonAnywhere:
   - Vá para a guia "Web"
   - Clique em "Add a new web app"
   - Escolha o domínio (geralmente username.pythonanywhere.com)
   - Selecione "Manual configuration"
   - Escolha "Python 3.10"
   - Configure o caminho virtual: `/home/SEU_USUARIO/TechCare/venv`
   - Configure o WSGI: edite o arquivo e substitua pelo conteúdo de `wsgi.py` do projeto
   - Configure os arquivos estáticos: URL: `/static/`, Directory: `/home/SEU_USUARIO/TechCare/app/static`

4. **Recarregar a aplicação web** clicando no botão "Reload" no painel Web

### 2. Deploy Manual

Se o método automatizado não funcionar ou você precisar de mais controle:

1. **Criar ambiente virtual no PythonAnywhere**:
   ```bash
   cd ~
   mkdir TechCare
   cd TechCare
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip setuptools wheel
   ```

2. **Fazer upload do código**:
   - Use a guia "Files" do PythonAnywhere ou git clone
   - Ou compacte o projeto e faça upload pelo console

3. **Instalar dependências**:
   ```bash
   python fix_pandas_pythonanywhere.py
   ```

4. **Configurar aplicação web** conforme descrito no método automatizado

## Solução de Problemas

### A aplicação não inicia ou retorna erro 500

1. **Verificar logs**:
   - Vá para a guia "Web" > "Logs"
   - Verifique "Error log" e "Server log"

2. **Problemas com imports**:
   - Verifique se todos os pacotes estão instalados corretamente
   - Rode manualmente: `pip install -r requirements_pythonanywhere_updated.txt`

3. **Problemas com pandas**:
   - Execute `python fix_pandas_pythonanywhere.py` para resolver

4. **Problemas com permissões de arquivos**:
   - Verifique permissões: `ls -la`
   - Corrija se necessário: `chmod -R 755 .`

5. **Problemas com caminhos**:
   - Verifique se o arquivo WSGI está configurado com os caminhos corretos
   - Verifique a configuração do env virtual no painel "Web"

## Manutenção

### Atualizar a aplicação

1. **Upload de novas versões**:
   ```bash
   python upload_to_pythonanywhere.py --username SEU_USUARIO --token SEU_TOKEN_API --files
   ```
   Isso fará o upload apenas dos arquivos, sem reconfigurar o ambiente.

2. **Recarregar a aplicação**:
   - Use o botão "Reload" no painel Web
   - Ou via API: `requests.post(f"https://www.pythonanywhere.com/api/v0/user/{username}/webapps/{domain}/reload/")`

## Referências

- [Documentação PythonAnywhere](https://help.pythonanywhere.com/)
- [API PythonAnywhere](https://help.pythonanywhere.com/pages/API/)
- [Fórum PythonAnywhere](https://www.pythonanywhere.com/forums/) 