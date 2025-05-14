# TechCare Admin API - Documentação

## 🚀 Visão Geral

Esta documentação descreve os endpoints da API do painel administrativo TechCare.

## 🔒 Autenticação

Todos os endpoints requerem autenticação via JWT (JSON Web Token). Inclua o token no cabeçalho de autorização:

```
Authorization: Bearer <seu_token_jwt>
```

## 📋 Endpoints Disponíveis

### Usuários

- `GET /usuarios`: Lista todos os usuários
- `POST /usuarios`: Cria um novo usuário

### Serviços

- `GET /servicos`: Lista o status de todos os serviços
- `POST /servicos`: Iniciar, parar ou reiniciar um serviço

## 🛠 Ferramentas e Tecnologias

- Especificação: OpenAPI 3.0.0
- Formato: YAML
- Geração de Documentação: Swagger/ReDoc

## 🔍 Como Usar

1. Instale uma ferramenta de visualização de OpenAPI (ex: Swagger UI)
2. Carregue o arquivo `api_docs.yaml`
3. Explore os endpoints interativamente

## ⚠️ Avisos

- Todos os endpoints são protegidos
- Somente usuários autorizados podem acessar
- Respeite os níveis de permissão

## 📞 Suporte

Em caso de dúvidas, entre em contato:
- Email: suporte@techcare.com
