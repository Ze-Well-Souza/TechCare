# Lista de Verificações Finais antes do Lançamento

Esta checklist foi atualizada com base nos problemas específicos encontrados durante tentativas anteriores de deploy.

## 1. Verificação do Virtualenv

- [ ] O virtualenv foi criado com Python 3.10 específico (`python3.10 -m venv venv`)
- [ ] O caminho do virtualenv no painel web está correto (`/home/Zewell10/TechCare/venv`)
- [ ] O Flask está instalado no virtualenv (verificado com `venv/bin/pip list | grep Flask`)
- [ ] As dependências essenciais foram instaladas primeiro, antes das outras

## 2. Verificação do Arquivo WSGI

- [ ] O caminho da aplicação está correto (`/home/Zewell10/TechCare`)
- [ ] O tratamento para simulação do pandas está implementado
- [ ] A importação da aplicação (`from app import create_app`) está funcionando
- [ ] O objeto `application` está sendo criado corretamente

## 3. Verificação da Estrutura de Diretórios

- [ ] O diretório `/home/Zewell10/TechCare` existe
- [ ] O diretório `/home/Zewell10/TechCare/app` existe e contém `__init__.py`
- [ ] Os arquivos estáticos estão em `/home/Zewell10/TechCare/app/static`
- [ ] As configurações estão em `/home/Zewell10/TechCare/config.py`

## 4. Configuração da Aplicação Web

- [ ] Source code: `/home/Zewell10/TechCare`
- [ ] Working directory: `/home/Zewell10/TechCare`
- [ ] WSGI configuration file: Conteúdo verificado e correto
- [ ] Virtualenv: `/home/Zewell10/TechCare/venv`
- [ ] Static files: URL `/static/` → Directory `/home/Zewell10/TechCare/app/static`

## 5. Verificação dos Logs

Após clicar em "Reload", verifique imediatamente:

- [ ] Error log - Sem erros de importação (especialmente `ModuleNotFoundError`)
- [ ] Server log - Confirmação de que a aplicação foi carregada

## 6. Verificação de Problemas Específicos Resolvidos

- [ ] Problema "No module named 'app'" - Resolvido pela configuração correta de caminhos
- [ ] Problema "No module named 'flask'" - Resolvido pela instalação correta no virtualenv
- [ ] Problema "OSError: [Errno 122]" - Resolvido pela simulação do pandas

## 7. Teste de Acesso e Funcionalidade

- [ ] A aplicação está acessível em `https://zewell10.pythonanywhere.com`
- [ ] A página de login é exibida corretamente
- [ ] Os arquivos estáticos (CSS, JS, imagens) estão sendo carregados
- [ ] É possível fazer login com as credenciais de administrador

## 8. Comandos Úteis para Solução de Problemas

### Testar se o Flask está instalado:
```bash
source ~/TechCare/venv/bin/activate
python -c "import flask; print(flask.__version__)"
```

### Testar a importação da aplicação:
```bash
source ~/TechCare/venv/bin/activate
cd ~/TechCare
python -c "from app import create_app; print('OK')"
```

### Verificar o espaço em disco disponível:
```bash
du -sh ~
```

### Verificar a estrutura do projeto:
```bash
find ~/TechCare/app -type f -name "__init__.py"
```

## 9. Erros Comuns e Soluções

### Erro: ModuleNotFoundError: No module named 'app'
**Solução**: 
1. Verifique se o caminho no arquivo WSGI está correto
2. Verifique se a pasta `app` existe no diretório do projeto
3. Verifique se a pasta `app` contém um arquivo `__init__.py`

### Erro: ModuleNotFoundError: No module named 'flask'
**Solução**:
1. Verifique se o caminho do virtualenv está correto
2. Reinstale o Flask no virtualenv: `pip install flask`
3. Verifique se o virtualenv está sendo usado pelo WSGI

### Erro: OSError: [Errno 122] Disk quota exceeded
**Solução**:
1. Use o simulador de pandas implementado nos passos anteriores
2. Remova arquivos desnecessários para liberar espaço
3. Utilize requirements_minimal.txt em vez do requirements.txt completo 