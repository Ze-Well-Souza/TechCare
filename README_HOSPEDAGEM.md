# Guia de Hospedagem do TechCare

Este guia fornece instruções para compartilhar sua aplicação TechCare com outras pessoas.

## Opção 1: Hospedagem Temporária com Ngrok (Mais Rápida)

Esta é a maneira mais rápida de compartilhar a aplicação, ideal para demonstrações ou análises temporárias.

### Pré-requisitos
- Python 3.8+ instalado
- Conexão com a internet

### Passos para Compartilhamento Rápido

1. **Instalar as ferramentas necessárias:**
   ```
   Execute o arquivo "instalar_ngrok.bat"
   ```

2. **Iniciar a aplicação com URL pública:**
   ```
   python run_with_ngrok.py
   ```

3. **Compartilhar o link:**
   Após a inicialização, um link será exibido no terminal (algo como `https://xxxx-xx-xx-xx.ngrok-free.app`).
   Compartilhe este link com quem desejar que acesse a aplicação.

### Limitações
- O túnel Ngrok fica ativo apenas enquanto seu computador estiver ligado e o script rodando
- O link muda cada vez que você reinicia a aplicação (versão gratuita)
- Limitações de banda na versão gratuita

## Opção 2: Hospedagem em Plataforma (Mais Permanente)

Para uma solução mais permanente, você pode hospedar o TechCare em uma plataforma de hospedagem.

### PythonAnywhere (Recomendado para Iniciantes)

1. Crie uma conta em [PythonAnywhere](https://www.pythonanywhere.com/)
2. Faça upload do código ou use Git para clonar o repositório
3. Configure um novo aplicativo web Flask apontando para `wsgi.py`
4. Configure as variáveis de ambiente:
   - `FLASK_CONFIG=production`
   - `SECRET_KEY=chave-secreta-forte`
5. Instale as dependências com o gerenciador de pacotes

### Railway ou Heroku

1. Crie um arquivo `Procfile` na raiz com o conteúdo: `web: gunicorn wsgi:app`
2. Configure uma conta em [Railway](https://railway.app/) ou [Heroku](https://heroku.com)
3. Faça upload do código ou conecte ao seu repositório Git
4. Configure variáveis de ambiente para produção
5. Execute o deploy

### VPS (Opção Avançada)

Para controle total sobre o ambiente:

1. Configure um servidor Linux (Ubuntu/Debian recomendado)
2. Instale as dependências necessárias
3. Configure Nginx como proxy reverso
4. Execute a aplicação com Gunicorn
5. Configure HTTPS com Let's Encrypt

## Configurações Adicionais para Produção

Quando hospedar em um ambiente permanente, considere:

1. **Banco de Dados:**
   - Migrar para PostgreSQL (recomendado para produção)
   - Configurar backups automáticos

2. **Segurança:**
   - Configurar HTTPS
   - Implementar rate limiting
   - Utilizar variáveis de ambiente para dados sensíveis
   - Configurar firewall

3. **Monitoramento:**
   - Configurar sistema de logs
   - Implementar alertas para erros críticos

## Suporte

Para dúvidas ou suporte adicional, entre em contato com:
- Email: contato@techcare.com.br
- Fórum de Suporte: [forum.techcare.com.br](https://forum.techcare.com.br) 