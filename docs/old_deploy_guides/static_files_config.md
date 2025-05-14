# Configuração de Arquivos Estáticos no PythonAnywhere

Na seção "Static files" da configuração da sua aplicação web no PythonAnywhere, adicione os seguintes mapeamentos:

| URL | Directory |
|-----|-----------|
| /static/ | /home/zewell10/TechCare/app/static |

## Como adicionar:

1. Na página "Web", localize a seção "Static files"
2. No campo "URL", digite: `/static/`
3. No campo "Directory", digite: `/home/zewell10/TechCare/app/static`
4. Clique no botão "Add"

Esta configuração garante que o Flask possa servir corretamente os arquivos CSS, JavaScript e imagens da sua aplicação.

## Verificação

Para verificar se os arquivos estáticos estão sendo servidos corretamente, após iniciar a aplicação, tente acessar:

```
https://zewell10.pythonanywhere.com/static/css/style.css
```

Se você ver o conteúdo do arquivo CSS, a configuração está correta. 