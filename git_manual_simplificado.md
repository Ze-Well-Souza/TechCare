# Guia Simplificado: Git e GitHub para o Projeto TechCare

Este é um guia simplificado para configurar o Git e fazer o primeiro push do projeto TechCare para o GitHub.

## Passo 1: Verificar se o Git está instalado

```
git --version
```

Se o comando não for reconhecido, você precisa instalar o Git:

1. Baixe o instalador em: https://git-scm.com/download/win
2. Execute o instalador e aceite as configurações padrão
3. Reinicie o PowerShell/CMD após a instalação

## Passo 2: Configurar o Git

Configure seu nome e email:

```
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@exemplo.com"
```

## Passo 3: Inicializar o repositório Git

Navegue até a pasta do projeto TechCare e execute:

```
git init
```

## Passo 4: Criar o .gitignore

Execute:

```
python cleanup_project.py --update-gitignore --yes
```

## Passo 5: Adicionar arquivos ao repositório

```
git add .
```

## Passo 6: Fazer o primeiro commit

```
git commit -m "Commit inicial do projeto TechCare"
```

## Passo 7: Criar um repositório no GitHub

1. Acesse https://github.com/
2. Clique em "+" no canto superior direito e selecione "New repository"
3. Nome do repositório: `techcare`
4. Descrição: "Sistema de Manutenção e Diagnóstico de Computadores"
5. Escolha a visibilidade (público ou privado)
6. Clique em "Create repository"

## Passo 8: Conectar o repositório local ao GitHub

Copie a URL do seu repositório (https://github.com/Ze-Well-Souza/TechCare) e execute:

```
git remote add origin https://github.com/Ze-Well-Souza/TechCare
```

## Passo 9: Enviar o código para o GitHub

```
git branch -M main
git push -u origin main
```

Quando solicitado, insira seu nome de usuário e senha do GitHub.

> **Nota**: Se você usa autenticação de dois fatores (2FA) no GitHub, em vez da senha, você precisará usar um token de acesso pessoal. Você pode gerar um em GitHub > Settings > Developer settings > Personal access tokens.

## Passo 10: Verificar se deu certo

Acesse https://github.com/seu-usuario/techcare para verificar se seu código foi enviado.

---

## Comandos úteis para o dia a dia

```
# Ver alterações pendentes
git status

# Atualizar seu repositório local
git pull origin main

# Enviar alterações para o GitHub
git add .
git commit -m "Descrição das alterações"
git push origin main
``` 