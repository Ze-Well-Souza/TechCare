# Pacote de Deploy do TechCare para PythonAnywhere

Este pacote contém os arquivos necessários para fazer o deploy do sistema TechCare no PythonAnywhere.

## Arquivos Incluídos

- `README_HOSPEDAGEM_PYTHONANYWHERE.md`: Guia detalhado passo a passo
- `requirements_pythonanywhere.txt`: Dependências para ambiente de produção
- `wsgi.py`: Arquivo WSGI principal do projeto
- `wsgi_pythonanywhere_example.py`: Exemplo de configuração do WSGI no PythonAnywhere
- `setup_pythonanywhere.py`: Script para inicializar o ambiente
- `create_admin_pythonanywhere.py`: Script para criar um usuário administrador

## Passos Rápidos para Deploy

1. Faça upload deste pacote e do código-fonte do projeto para o PythonAnywhere
2. Descompacte os arquivos no servidor
3. Crie e ative um ambiente virtual: `mkvirtualenv --python=python3.9 techcare-venv`
4. Instale as dependências: `pip install -r requirements_pythonanywhere.txt`
5. Execute o script de configuração: `python setup_pythonanywhere.py`
6. Configure a aplicação web conforme o guia
7. Configure o arquivo WSGI conforme o exemplo fornecido
8. Clique em "Reload" para iniciar a aplicação
9. Crie um usuário administrador: `python create_admin_pythonanywhere.py`

Para instruções detalhadas, consulte o arquivo `README_HOSPEDAGEM_PYTHONANYWHERE.md`.

## Observações Importantes

- A chave secreta (`SECRET_KEY`) está configurada no arquivo WSGI exemplo
- Certifique-se de que todos os diretórios de dados são criados corretamente
- Configure o mapeamento de arquivos estáticos na interface do PythonAnywhere

Para dúvidas ou suporte adicional, entre em contato com a equipe de desenvolvimento.

---

TechCare © 2024 