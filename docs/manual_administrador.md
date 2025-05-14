# Manual do Administrador - TechCare

Este manual contém informações detalhadas para administradores do sistema TechCare, incluindo configurações, manutenção, monitoramento e procedimentos de solução de problemas.

## Índice

1. [Introdução](#introdução)
2. [Acesso Administrativo](#acesso-administrativo)
   - [Criar Conta de Administrador](#criar-conta-de-administrador)
   - [Painel de Administração](#painel-de-administração)
3. [Gerenciamento de Usuários](#gerenciamento-de-usuários)
   - [Visualizar Usuários](#visualizar-usuários)
   - [Editar Perfis](#editar-perfis)
   - [Gerenciar Permissões](#gerenciar-permissões)
4. [Configurações do Sistema](#configurações-do-sistema)
   - [Configurações Gerais](#configurações-gerais)
   - [Configurações de Email](#configurações-de-email)
   - [Integração com Serviços Externos](#integração-com-serviços-externos)
5. [Monitoramento e Diagnóstico](#monitoramento-e-diagnóstico)
   - [Painel de Métricas](#painel-de-métricas)
   - [Logs do Sistema](#logs-do-sistema)
   - [Alertas e Notificações](#alertas-e-notificações)
6. [Manutenção do Sistema](#manutenção-do-sistema)
   - [Backup e Restauração](#backup-e-restauração)
   - [Atualização do Sistema](#atualização-do-sistema)
   - [Limpeza de Dados](#limpeza-de-dados)
7. [Segurança](#segurança)
   - [Política de Senhas](#política-de-senhas)
   - [Registros de Auditoria](#registros-de-auditoria)
   - [Configuração de Firewall](#configuração-de-firewall)
8. [Solução de Problemas](#solução-de-problemas)
   - [Problemas Comuns](#problemas-comuns)
   - [Ferramentas de Diagnóstico](#ferramentas-de-diagnóstico)
9. [Referência Técnica](#referência-técnica)
   - [Arquitetura do Sistema](#arquitetura-do-sistema)
   - [API de Administração](#api-de-administração)

## Introdução

O TechCare é uma plataforma de diagnóstico e manutenção de computadores. Este manual destina-se aos administradores do sistema e fornece instruções detalhadas sobre como configurar, monitorar e manter a plataforma, além de gerenciar usuários e solucionar problemas.

## Acesso Administrativo

### Criar Conta de Administrador

A primeira conta de administrador é criada durante a instalação inicial do sistema. Para criar contas de administrador adicionais:

1. Faça login com uma conta de administrador existente.
2. Acesse o painel de administração.
3. Navegue até "Usuários" > "Adicionar Usuário".
4. Preencha o formulário com os dados do novo administrador.
5. No campo "Papel", selecione "Administrador".
6. Clique em "Criar Usuário".

Alternativamente, é possível promover um usuário existente a administrador:

1. Navegue até "Usuários" > "Listar Usuários".
2. Localize o usuário desejado e clique em "Editar".
3. Altere o campo "Papel" para "Administrador".
4. Clique em "Salvar Alterações".

### Painel de Administração

Para acessar o painel de administração:

1. Faça login com uma conta de administrador.
2. Clique no seu nome de usuário no canto superior direito.
3. Selecione "Painel de Administração" no menu suspenso.

O painel de administração inclui as seguintes seções:

- **Visão Geral**: Dashboard com métricas e estatísticas do sistema.
- **Usuários**: Gerenciamento de contas de usuário.
- **Diagnósticos**: Acesso a todos os diagnósticos realizados no sistema.
- **Configurações**: Configurações gerais do sistema.
- **Logs**: Visualização dos logs do sistema.
- **Sistema**: Informações e ferramentas de manutenção do sistema.

## Gerenciamento de Usuários

### Visualizar Usuários

Para visualizar todos os usuários do sistema:

1. No painel de administração, navegue até "Usuários" > "Listar Usuários".
2. A tabela exibirá informações sobre cada usuário:
   - Nome de usuário
   - Email
   - Papel (usuário, técnico, administrador)
   - Status (ativo/inativo)
   - Data de criação
   - Último login

Você pode filtrar e pesquisar usuários por nome, email ou papel.

### Editar Perfis

Para editar as informações de um usuário:

1. Na lista de usuários, clique no botão "Editar" ao lado do usuário desejado.
2. Modifique os campos necessários:
   - Nome
   - Email
   - Papel
   - Status
3. Clique em "Salvar Alterações".

### Gerenciar Permissões

Para gerenciar as permissões de usuários:

1. Navegue até "Usuários" > "Papéis e Permissões".
2. Selecione o papel que deseja modificar (usuário, técnico, administrador).
3. Marque ou desmarque as permissões específicas para esse papel.
4. Clique em "Salvar Permissões".

Os papéis padrão incluem:
- **Usuário**: Acesso básico para executar diagnósticos e reparos no próprio sistema.
- **Técnico**: Acesso para gerenciar diagnósticos e reparos de múltiplos usuários.
- **Administrador**: Acesso completo a todas as funcionalidades do sistema.

## Configurações do Sistema

### Configurações Gerais

Para ajustar as configurações gerais do sistema:

1. No painel de administração, navegue até "Configurações" > "Geral".
2. Ajuste as seguintes configurações:
   - **Nome do Sistema**: Nome personalizado para sua instalação do TechCare.
   - **URL Base**: URL base para o sistema (usado em emails e notificações).
   - **Idioma Padrão**: Idioma padrão para novos usuários.
   - **Fuso Horário**: Fuso horário para exibição de datas e agendamentos.
   - **Limites de Uso**: Configurações para limitar o uso de recursos.
3. Clique em "Salvar Configurações".

### Configurações de Email

Para configurar o envio de emails pelo sistema:

1. Navegue até "Configurações" > "Email".
2. Configure os parâmetros do servidor SMTP:
   - Servidor SMTP
   - Porta
   - Nome de usuário
   - Senha
   - Método de criptografia (TLS/SSL)
   - Endereço de email do remetente
   - Nome do remetente
3. Clique em "Testar Configuração" para enviar um email de teste.
4. Após verificar que o email foi recebido corretamente, clique em "Salvar Configurações".

### Integração com Serviços Externos

O TechCare pode ser integrado a serviços externos para funcionalidades adicionais:

1. Navegue até "Configurações" > "Integrações".
2. Configure as seguintes integrações disponíveis:
   - **Base de Conhecimento**: Integração com sistemas de base de conhecimento.
   - **Sistema de Tickets**: Integração com sistemas de helpdesk.
   - **Serviços de Nuvem**: Para backup e armazenamento de dados.
   - **Serviços de Notificação**: Para envio de notificações push ou SMS.
3. Para cada serviço, forneça as credenciais de API necessárias.
4. Clique em "Testar Conexão" para verificar a integração.
5. Clique em "Salvar" após configurar cada integração.

## Monitoramento e Diagnóstico

### Painel de Métricas

O painel de métricas fornece uma visão geral do uso e desempenho do sistema:

1. No painel de administração, navegue até "Sistema" > "Métricas".
2. O painel exibe as seguintes informações:
   - **Uso do Servidor**: CPU, memória e disco.
   - **Atividade de Usuários**: Usuários ativos, logins por hora.
   - **Diagnósticos**: Quantidade de diagnósticos por dia/semana/mês.
   - **Reparos**: Quantidade de reparos executados.
   - **Tempo de Resposta**: Tempo médio de resposta da aplicação.

Você pode ajustar o intervalo de tempo para visualizar métricas históricas.

### Logs do Sistema

Para visualizar os logs do sistema:

1. Navegue até "Sistema" > "Logs".
2. Selecione o tipo de log que deseja visualizar:
   - **Aplicação**: Logs gerais da aplicação.
   - **Acesso**: Logs de acesso e autenticação.
   - **Erro**: Logs de erros e exceções.
   - **Auditoria**: Logs de ações administrativas.
3. Use os filtros disponíveis para refinar os resultados:
   - Nível de log (INFO, WARNING, ERROR, CRITICAL)
   - Intervalo de datas
   - Usuário
   - Módulo
4. Clique em "Exportar" para baixar os logs em formato CSV ou JSON.

### Alertas e Notificações

Configure alertas para ser notificado sobre eventos importantes:

1. Navegue até "Sistema" > "Alertas".
2. Clique em "Adicionar Alerta".
3. Configure os parâmetros do alerta:
   - **Tipo**: Tipo de evento para monitorar (uso de CPU, espaço em disco, etc.).
   - **Condição**: Condição que ativa o alerta (CPU > 90%, disco < 10%, etc.).
   - **Canal**: Método de notificação (email, SMS, webhook).
   - **Destinatários**: Quem receberá o alerta.
   - **Severidade**: Nível de importância do alerta.
4. Clique em "Salvar Alerta".

## Manutenção do Sistema

### Backup e Restauração

Para configurar backup automático do sistema:

1. Navegue até "Sistema" > "Backup".
2. Configure as opções de backup:
   - **Frequência**: Diária, semanal ou mensal.
   - **Hora**: Horário para execução do backup.
   - **Retenção**: Número de backups a manter.
   - **Destino**: Local de armazenamento (local, FTP, S3, etc.).
   - **Conteúdo**: Componentes a incluir no backup (banco de dados, arquivos, configurações).
3. Clique em "Salvar Configuração".

Para restaurar um backup:

1. Navegue até "Sistema" > "Backup" > "Restaurar".
2. Selecione o backup a ser restaurado da lista de backups disponíveis.
3. Clique em "Restaurar" e confirme a operação.

### Atualização do Sistema

Para atualizar o TechCare:

1. Navegue até "Sistema" > "Atualização".
2. O sistema verificará se há atualizações disponíveis.
3. Se houver atualizações, clique em "Baixar Atualização".
4. Após o download, clique em "Instalar Atualização".
5. O sistema fará backup automático antes da atualização.
6. Siga as instruções na tela para concluir a atualização.

### Limpeza de Dados

Para limpar dados antigos e otimizar o desempenho do sistema:

1. Navegue até "Sistema" > "Manutenção" > "Limpeza de Dados".
2. Selecione os tipos de dados a serem limpos:
   - **Logs antigos**: Logs com mais de X dias.
   - **Diagnósticos antigos**: Diagnósticos com mais de X dias/meses.
   - **Arquivos temporários**: Arquivos temporários não utilizados.
   - **Sessões expiradas**: Dados de sessão obsoletos.
3. Especifique o período para cada tipo de dado (ex: logs mais antigos que 30 dias).
4. Clique em "Iniciar Limpeza" e confirme a operação.

## Segurança

### Política de Senhas

Para configurar a política de senhas do sistema:

1. Navegue até "Configurações" > "Segurança" > "Política de Senhas".
2. Configure os seguintes parâmetros:
   - **Comprimento mínimo**: Número mínimo de caracteres.
   - **Complexidade**: Requisitos de complexidade (maiúsculas, minúsculas, números, símbolos).
   - **Histórico**: Número de senhas anteriores que não podem ser reutilizadas.
   - **Expiração**: Período após o qual a senha deve ser alterada.
   - **Tentativas de login**: Número máximo de tentativas antes do bloqueio da conta.
   - **Duração do bloqueio**: Tempo que a conta permanece bloqueada após tentativas falhas.
3. Clique em "Salvar Configurações".

### Registros de Auditoria

Para visualizar os registros de auditoria:

1. Navegue até "Sistema" > "Segurança" > "Registros de Auditoria".
2. Os registros mostram todas as ações administrativas realizadas no sistema:
   - Data e hora
   - Usuário
   - Ação realizada
   - Endereço IP
   - Resultado (sucesso/falha)
3. Use os filtros disponíveis para refinar os resultados.
4. Clique em "Exportar" para baixar os registros em formato CSV ou JSON.

### Configuração de Firewall

Para configurar regras de firewall da aplicação:

1. Navegue até "Configurações" > "Segurança" > "Firewall da Aplicação".
2. Configure as seguintes opções:
   - **Limite de taxa**: Número máximo de requisições permitidas por IP em um período.
   - **Lista de bloqueio**: IPs ou intervalos de IPs bloqueados.
   - **Lista de permissão**: IPs ou intervalos de IPs sempre permitidos.
   - **Proteção contra ataques**: Ative ou desative proteções específicas (XSS, CSRF, injeção SQL).
3. Clique em "Salvar Configurações".

## Solução de Problemas

### Problemas Comuns

#### O Sistema Está Lento

1. Verifique o uso de recursos no painel de métricas.
2. Verifique o tamanho do banco de dados e considere otimizá-lo.
3. Verifique os logs de erro para problemas específicos.
4. Considere aumentar os recursos do servidor se necessário.

#### Emails Não Estão Sendo Enviados

1. Verifique as configurações de SMTP em "Configurações" > "Email".
2. Teste a configuração de email usando o botão "Testar Configuração".
3. Verifique os logs de erro para mensagens específicas relacionadas ao envio de email.
4. Confirme que seu servidor SMTP permite envios do IP do servidor TechCare.

#### Erros de Banco de Dados

1. Verifique a conexão com o banco de dados.
2. Verifique o espaço disponível no servidor de banco de dados.
3. Execute a manutenção do banco de dados em "Sistema" > "Banco de Dados" > "Manutenção".
4. Verifique os logs de erro para mensagens específicas relacionadas ao banco de dados.

### Ferramentas de Diagnóstico

Para diagnosticar problemas do sistema:

1. Navegue até "Sistema" > "Ferramentas" > "Diagnóstico".
2. As seguintes ferramentas estão disponíveis:
   - **Verificação de Integridade**: Verifica a integridade dos arquivos do sistema.
   - **Teste de Banco de Dados**: Testa a conexão e o desempenho do banco de dados.
   - **Teste de Email**: Testa a configuração de email.
   - **Verificação de Dependências**: Verifica se todas as dependências estão instaladas e funcionando.
   - **Informações do Sistema**: Exibe informações detalhadas sobre o ambiente de execução.
3. Selecione a ferramenta desejada e clique em "Executar".
4. Analise os resultados e siga as recomendações para resolver os problemas encontrados.

## Referência Técnica

### Arquitetura do Sistema

O TechCare segue uma arquitetura em camadas:

1. **Interface de Usuário**: Frontend desenvolvido em HTML, CSS e JavaScript.
2. **Camada de Aplicação**: Backend em Python utilizando o framework Flask.
3. **Camada de Serviços**: Serviços específicos para diagnóstico, reparo, etc.
4. **Camada de Dados**: Banco de dados SQL (PostgreSQL em produção, SQLite para desenvolvimento).

Os principais componentes incluem:

- **Servidor Web**: Nginx como proxy reverso.
- **Servidor de Aplicação**: Gunicorn como servidor WSGI.
- **ORM**: SQLAlchemy para mapeamento objeto-relacional.
- **Autenticação**: Flask-Login para gerenciamento de sessões.
- **Tarefas Assíncronas**: Celery para processamento de tarefas em segundo plano.

### API de Administração

A API de administração permite automatizar tarefas administrativas:

Para acessar a documentação completa da API:

1. Navegue até "Sistema" > "API" > "Documentação".
2. A documentação interativa da API será exibida, permitindo testar endpoints diretamente.

Para obter um token de API:

1. Navegue até "Sistema" > "API" > "Tokens".
2. Clique em "Gerar Novo Token".
3. Forneça uma descrição para o token e selecione as permissões necessárias.
4. Clique em "Criar Token".
5. Copie o token gerado (ele será exibido apenas uma vez).

Exemplo de uso da API com curl:

```bash
curl -X GET "https://seu-servidor/api/admin/users" \
  -H "Authorization: Bearer seu_token_aqui" \
  -H "Content-Type: application/json"
``` 