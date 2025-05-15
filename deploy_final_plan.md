# Plano de Deploy Final no PythonAnywhere

## Visão Geral

Este documento descreve o processo detalhado para realizar o deploy final da aplicação TechCare no PythonAnywhere, garantindo que todas as funcionalidades estejam operacionais no ambiente de produção.

## Pré-requisitos

- Conta PythonAnywhere (de preferência paga para recursos adequados)
- Acesso git ao repositório do projeto
- Todos os testes passando localmente (`python run_complete_test_suite.py`)
- Scripts de deploy preparados (`upload_to_pythonanywhere.py`, etc.)

## Etapas do Deploy

### 1. Preparação do Código para Deploy

1. **Criar pacote de deploy**
   ```bash
   python create_deploy_package.py
   ```
   Este script irá:
   - Executar testes para garantir estabilidade
   - Gerar versão otimizada dos arquivos estáticos
   - Limpar arquivos desnecessários (cache, __pycache__, etc.)
   - Criar arquivo zip com todos os arquivos necessários

2. **Verificar prontidão para deploy**
   ```bash
   python check_deploy_readiness.py
   ```
   Este script verifica:
   - Compatibilidade com bibliotecas do PythonAnywhere
   - Configurações específicas para produção
   - Scripts de migração/inicialização do banco

### 2. Upload e Configuração Inicial no PythonAnywhere

1. **Upload automático do pacote**
   ```bash
   python upload_to_pythonanywhere.py --username SEU_USUARIO --password SUA_SENHA
   ```
   
   Alternativa manual:
   - Fazer login no PythonAnywhere
   - Ir para a seção Files
   - Fazer upload do arquivo ZIP gerado
   - Extrair no diretório `/home/{username}/techcare`

2. **Acessar console bash no PythonAnywhere**
   - Ir para a seção Consoles
   - Iniciar um novo console Bash

3. **Configurar ambiente virtual**
   ```bash
   cd /home/{username}/techcare
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements_pythonanywhere_fixed.txt
   ```

4. **Configurar variáveis de ambiente**
   - Editar o arquivo `.pythonanywhere.txt` com as variáveis necessárias
   - Executar:
   ```bash
   cp .pythonanywhere.txt ~/.bashrc.d/techcare.sh
   chmod +x ~/.bashrc.d/techcare.sh
   source ~/.bashrc.d/techcare.sh
   ```

### 3. Configuração do Banco de Dados

1. **Inicializar o banco de dados**
   ```bash
   cd /home/{username}/techcare
   python update_database_schema.py
   ```

2. **Criar usuário administrador inicial**
   ```bash
   python create_admin_pythonanywhere.py
   ```

3. **Verificar estrutura do banco**
   ```bash
   python -c "from app import db; print('Tabelas criadas: ' + ', '.join([t.name for t in db.metadata.tables.values()]))"
   ```

### 4. Configuração da Aplicação Web

1. **Configurar aplicação web no PythonAnywhere**
   - Ir para a seção Web
   - Clicar em "Add a new web app"
   - Escolher "Manual configuration"
   - Selecionar Python 3.12
   - Configurar diretório de código: `/home/{username}/techcare`
   - Configurar working directory: `/home/{username}/techcare`

2. **Configurar arquivo WSGI**
   - Editar o arquivo WSGI no PythonAnywhere
   - Substituir pelo conteúdo de `wsgi_pythonanywhere.py`

3. **Configurar arquivos estáticos**
   - Em "Static Files"
   - Adicionar URL: `/static/`
   - Caminho: `/home/{username}/techcare/app/static`

### 5. Configurações Finais e Testes

1. **Reiniciar a aplicação web**
   - Clicar em "Reload {username}.pythonanywhere.com"

2. **Verificar logs de inicialização**
   - Clicar em "View log files"
   - Verificar "Error log" por problemas de inicialização

3. **Executar verificações de integridade**
   ```bash
   curl https://{username}.pythonanywhere.com/api/health
   ```

4. **Testar todas as principais funcionalidades**
   - Autenticação
   - Realização de diagnóstico
   - Geração de relatórios
   - Limpeza de sistema
   - Atualização de drivers

### 6. Monitoramento Pós-deploy

1. **Configurar monitoramento**
   - Implementar script `monitor_pythonanywhere.py` para verificações periódicas

2. **Verificar logs continuamente**
   ```bash
   python monitor_logs.py --days 2
   ```

3. **Realizar backup inicial do banco de dados**
   ```bash
   python backup_database.py --env production
   ```

## Rollback (Em caso de falha)

1. **Prepare um plano de rollback**
   - Manter versão anterior do código disponível
   - Ter backup do banco de dados antes do deploy

2. **Procedimento de rollback**
   ```bash
   cd /home/{username}/techcare
   git reset --hard HEAD~1  # Voltar para commit anterior
   python restore_database.py --backup latest
   # Recarregar a aplicação web
   ```

## Verificação Final de Segurança

1. **Verificar configurações de segurança**
   ```bash
   python security_check.py --env production
   ```

2. **Verificar exposição de informações sensíveis**
   - Confirmar que não há chaves secretas expostas
   - Verificar se todos os endpoints requerem autenticação apropriada

## Documentação e Comunicação

1. **Atualizar documentação de produção**
   - Status do deploy
   - URL de acesso 
   - Credenciais de teste (em canal seguro)

2. **Comunicar finalização do deploy**
   - Informar stakeholders sobre conclusão do deploy
   - Compartilhar instruções de acesso e testes

## Diagrama de Fluxo do Deploy

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Preparação do  │     │    Upload e     │     │  Configuração   │
│  Código Local   │────►│   Configuração  │────►│ Banco de Dados  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                         │
┌─────────────────┐     ┌─────────────────┐     ┌───────▼─────────┐
│  Monitoramento  │     │   Verificação   │     │  Configuração   │
│   Pós-deploy    │◄────│     Final       │◄────│  Aplicação Web  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Checklist Final de Deploy

- [ ] Pacote de deploy criado e verificado
- [ ] Upload concluído para PythonAnywhere
- [ ] Ambiente virtual configurado corretamente
- [ ] Banco de dados inicializado e verificado
- [ ] Usuário administrador criado
- [ ] Configuração da aplicação web concluída
- [ ] Arquivos estáticos configurados corretamente
- [ ] Aplicação reiniciada e funcionando
- [ ] Verificações de integridade passando
- [ ] Testes manuais de funcionalidades principais concluídos
- [ ] Monitoramento configurado
- [ ] Backup inicial realizado
- [ ] Verificações de segurança concluídas
- [ ] Documentação atualizada
- [ ] Comunicação do deploy enviada

## Contatos para Suporte

- **Suporte PythonAnywhere**: support@pythonanywhere.com
- **Equipe de Desenvolvimento**: dev@techcare.com.br
- **Administrador do Sistema**: admin@techcare.com.br 