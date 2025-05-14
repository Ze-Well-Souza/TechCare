# Manual de Integração do TechCare com Git e GitHub

Este guia fornece instruções passo a passo para configurar o Git e integrar seu projeto TechCare com o GitHub.

## 📋 Índice

1. [Instalação do Git](#1-instalação-do-git)
2. [Configuração Inicial do Git](#2-configuração-inicial-do-git)
3. [Inicialização do Repositório Local](#3-inicialização-do-repositório-local)
4. [Criação de um Repositório no GitHub](#4-criação-de-um-repositório-no-github)
5. [Conexão do Repositório Local ao GitHub](#5-conexão-do-repositório-local-ao-github)
6. [Primeiro Commit e Push](#6-primeiro-commit-e-push)
7. [Fluxo de Trabalho Diário](#7-fluxo-de-trabalho-diário)
8. [Solução de Problemas Comuns](#8-solução-de-problemas-comuns)

---

## 1. Instalação do Git

### Método Automático (Recomendado)

1. Navegue até a pasta do seu projeto TechCare no PowerShell/CMD.
2. Execute o script de instalação:
   ```
   python install_git.py
   ```
3. Siga as instruções exibidas no terminal.

### Método Manual

1. Baixe o instalador do Git para Windows no [site oficial](https://git-scm.com/download/win).
2. Execute o instalador.
3. Aceite as configurações padrão, mas certifique-se de selecionar:
   - Na tela "Adjusting your PATH environment", escolha "Git from the command line and also from 3rd-party software"
   - Para editor padrão, recomendamos "Use Visual Studio Code as Git's default editor" (se tiver o VS Code instalado)
   - Para linha de comando, escolha "Use Git from the Windows Command Prompt"
4. Complete a instalação.
5. Feche e reabra o PowerShell/CMD.

### Verificando a Instalação

Execute o seguinte comando para verificar se o Git foi instalado corretamente:
```
git --version
```

Deve exibir algo como `git version 2.40.1.windows.1`.

---

## 2. Configuração Inicial do Git

Após instalar o Git, configure seu nome de usuário e e-mail que aparecerão nos seus commits:

```
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@exemplo.com"
```

Você pode verificar suas configurações com:
```
git config --list
```

---

## 3. Inicialização do Repositório Local

### Método Automático

1. Execute o script de limpeza com a opção de inicialização do Git:
   ```
   python cleanup_project.py --git-init
   ```

### Método Manual

1. Navegue até a pasta do seu projeto TechCare no PowerShell/CMD.
2. Execute:
   ```
   git init
   ```
3. Crie um arquivo `.gitignore` adequado (o script `cleanup_project.py` já faz isso para você).

---

## 4. Criação de um Repositório no GitHub

1. Acesse [GitHub](https://github.com/) e faça login.
2. Clique no botão "+" no canto superior direito e selecione "New repository".
3. Preencha os campos:
   - Repository name: `techcare` (ou outro nome de sua preferência)
   - Description: "Sistema de Manutenção e Diagnóstico de Computadores"
   - Visibilidade: Public ou Private (conforme sua preferência)
4. **NÃO** inicialize o repositório com README, .gitignore ou license (já temos isso localmente).
5. Clique em "Create repository".

---

## 5. Conexão do Repositório Local ao GitHub

Após criar o repositório no GitHub, você verá instruções para conectar seu repositório local.

### Método Automático

1. Execute o script de configuração do GitHub:
   ```
   python setup_github_repo.py
   ```
2. Quando solicitado, insira as informações do seu repositório GitHub.

### Método Manual

1. Copie a URL do seu repositório GitHub (formato: https://github.com/seu-usuario/techcare.git).
2. No PowerShell/CMD, adicione o remote:
   ```
   git remote add origin https://github.com/seu-usuario/techcare.git
   ```

---

## 6. Primeiro Commit e Push

### Método Automático

O script `setup_github_repo.py` já oferece a opção de fazer o primeiro commit e push.

### Método Manual

1. Adicione todos os arquivos ao stage:
   ```
   git add .
   ```

2. Faça o commit inicial:
   ```
   git commit -m "Commit inicial do projeto TechCare"
   ```

3. Configure o nome da branch principal (main é o padrão atual):
   ```
   git branch -M main
   ```

4. Faça o push para o GitHub:
   ```
   git push -u origin main
   ```

5. Quando solicitado, insira seu nome de usuário e senha do GitHub (ou token de acesso pessoal se 2FA estiver ativado).

---

## 7. Fluxo de Trabalho Diário

Após a configuração inicial, aqui está um fluxo de trabalho típico:

1. **Sempre sincronize antes de começar a trabalhar**:
   ```
   git pull origin main
   ```

2. **Faça suas alterações no código**

3. **Verifique o status das alterações**:
   ```
   git status
   ```

4. **Adicione as alterações ao stage**:
   ```
   git add .
   ```
   ou para arquivos específicos:
   ```
   git add caminho/para/arquivo
   ```

5. **Faça o commit das alterações**:
   ```
   git commit -m "Descrição clara do que foi alterado"
   ```

6. **Envie as alterações para o GitHub**:
   ```
   git push origin main
   ```

---

## 8. Solução de Problemas Comuns

### Erro de Credenciais

Se você receber erros de autenticação ao fazer push:

1. **Credenciais salvas incorretamente**:
   ```
   git config --global credential.helper manager-core
   ```
   e tente novamente o push.

2. **Usando 2FA no GitHub**:
   - Você precisará criar um token de acesso pessoal.
   - Acesse GitHub > Settings > Developer settings > Personal access tokens > Generate new token.
   - Marque as permissões necessárias (repo, workflow).
   - Use o token como senha ao fazer push.

### Conflitos de Merge

Se você receber um erro de conflito ao fazer pull:

1. Resolva os conflitos editando os arquivos marcados.
2. Adicione os arquivos resolvidos:
   ```
   git add .
   ```
3. Conclua o merge:
   ```
   git commit
   ```

### Git não encontrado no PATH

Se você instalou o Git, mas o comando `git` não é reconhecido:

1. Reinicie o PowerShell/CMD.
2. Se o problema persistir, adicione manualmente o Git ao PATH:
   - Localize o diretório de instalação do Git (geralmente `C:\Program Files\Git\cmd`).
   - Adicione ao PATH do sistema (Painel de Controle > Sistema > Configurações avançadas do sistema > Variáveis de ambiente).

---

## Comandos Git Úteis para Referência

```
# Ver histórico de commits
git log

# Ver alterações específicas
git diff

# Desfazer alterações não commitadas
git checkout -- <arquivo>

# Desfazer o último commit (mantendo as alterações)
git reset --soft HEAD~1

# Criar e mudar para uma nova branch
git checkout -b nome-da-branch

# Listar todas as branches
git branch

# Mudar de branch
git checkout nome-da-branch

# Mesclar uma branch na branch atual
git merge nome-da-branch
```

---

## Recursos Adicionais

- [Documentação oficial do Git](https://git-scm.com/doc)
- [Guia do GitHub](https://guides.github.com/)
- [Git Cheat Sheet](https://training.github.com/downloads/github-git-cheat-sheet.pdf)
- [Aprenda Git Interativamente](https://learngitbranching.js.org/) 