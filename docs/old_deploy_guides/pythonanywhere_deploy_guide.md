# Guia para Deploy do seu Projeto Flask no PythonAnywhere (Conta Gratuita)

Olá! Este guia vai te ajudar a colocar seu projeto no ar usando o PythonAnywhere.

## Arquivos Preparados para Você:

1.  **`requirements_pythonanywhere.txt`**: Contém a lista de pacotes Python que seu projeto precisa. Já ajustei para remover pacotes de teste e incluir os necessários para o Flask e suas extensões.
2.  **`wsgi_pythonanywhere_example.py`**: Um *exemplo* de como seu arquivo WSGI deve se parecer no PythonAnywhere. Você precisará editar o arquivo WSGI diretamente na interface do PythonAnywhere, usando este como base.

## Passos para o Deploy:

**1. Crie uma Conta e Faça Login no PythonAnywhere:**

*   Acesse [www.pythonanywhere.com](https://www.pythonanywhere.com) e crie uma conta gratuita ("Beginner"), caso ainda não tenha.
*   Faça login na sua conta.

**2. Faça o Upload dos Arquivos do seu Projeto:**

*   No painel do PythonAnywhere, vá para a aba "**Files**".
*   Crie um novo diretório para o seu projeto (por exemplo, `techcare_flask_app`).
*   Entre nesse diretório.
*   Faça o upload de **todos os arquivos e pastas** do seu projeto que estão dentro da pasta `techcare_python` (a pasta principal do seu código Flask, que contém `app/`, `run.py`, `requirements_pythonanywhere.txt`, etc.).
    *   **Importante:** Não envie a pasta `venv` que você tem localmente, nem a pasta `.pytest_cache` ou arquivos como `.coverage`.
    *   Certifique-se de que o arquivo `requirements_pythonanywhere.txt` (que eu preparei) seja enviado, e não o seu `requirements.txt` original, se ele contiver pacotes de teste ou específicos do Windows.

**3. Crie uma Nova Aplicação Web (Web App):**

*   No painel do PythonAnywhere, vá para a aba "**Web**".
*   Clique em "**Add a new web app**".
*   Siga os passos:
    *   Seu nome de domínio será algo como `seunome.pythonanywhere.com`. Clique em "Next".
    *   Selecione "**Flask**" como o framework Python.
    *   Selecione a versão do Python que deseja usar (por exemplo, Python 3.10 ou 3.11, se disponível e compatível com seu código). O PythonAnywhere geralmente sugere uma versão estável.
    *   Confirme o caminho para o seu projeto. Ele deve ser algo como `/home/seu_usuario_pythonanywhere/techcare_flask_app/run.py` (ajuste `seu_usuario_pythonanywhere` e `techcare_flask_app` conforme o seu nome de usuário e o nome do diretório que você criou).
*   Após a criação, você será redirecionado para a página de configuração da sua aplicação web.

**4. Configure o Ambiente Virtual (Virtualenv):**

*   Na página de configuração da sua aplicação web, role para baixo até a seção "**Virtualenv**".
*   Clique no link que diz algo como "**Start a console in this virtualenv**" ou insira o caminho do seu virtualenv (ex: `/home/seu_usuario_pythonanywhere/.virtualenvs/seunome.pythonanywhere.com`).
*   Isso abrirá um console (terminal) já dentro do ambiente virtual da sua aplicação web.
*   Dentro deste console, navegue até o diretório onde você fez o upload do seu projeto:
    ```bash
    cd /home/seu_usuario_pythonanywhere/techcare_flask_app
    ```
    (Lembre-se de substituir `seu_usuario_pythonanywhere` e `techcare_flask_app`)
*   Instale as dependências usando o arquivo que preparamos:
    ```bash
    pip install -r requirements_pythonanywhere.txt
    ```
*   Aguarde a instalação ser concluída. Se houver algum erro, verifique se o arquivo `requirements_pythonanywhere.txt` está correto e se todos os pacotes são compatíveis.

**5. Configure o Arquivo WSGI:**

*   Volte para a aba "**Web**" no painel do PythonAnywhere.
*   Na seção "**Code**", você verá um link para o seu "**WSGI configuration file**". O caminho será algo como `/var/www/seu_usuario_pythonanywhere_pythonanywhere_com_wsgi.py`.
*   Clique neste link para editar o arquivo.
*   **Substitua o conteúdo existente** pelo conteúdo similar ao do arquivo `wsgi_pythonanywhere_example.py` que eu forneci, fazendo as seguintes adaptações **CRUCIAIS**:
    *   Altere a linha `project_home = '/home/seu_usuario_pythonanywhere/caminho_para_seu_projeto'` para o caminho **real** do diretório do seu projeto no PythonAnywhere. Por exemplo:
        ```python
        project_home = '/home/SEU_NOME_DE_USUARIO/techcare_flask_app'
        ```
        (Substitua `SEU_NOME_DE_USUARIO` pelo seu nome de usuário no PythonAnywhere e `techcare_flask_app` pelo nome da pasta do seu projeto).
    *   Verifique se a linha `from run import app as application` está correta. Se o arquivo principal que cria sua instância Flask (`app = Flask(__name__)`) se chama `run.py` e a variável da aplicação é `app`, então está correto. Se for diferente (por exemplo, `main.py` ou a variável se chamar `server`), ajuste aqui.
*   Salve o arquivo WSGI.

**6. Configure os Diretórios de Arquivos Estáticos (Static Files) e Templates:**

*   Ainda na aba "**Web**", vá para a seção "**Static files**".
*   Clique em "**Add a new static file mapping**".
    *   Para o campo "**URL**", digite `/static` (exatamente assim).
    *   Para o campo "**Directory**", digite o caminho completo para a pasta `static` dentro do seu projeto. Exemplo:
        `/home/SEU_NOME_DE_USUARIO/techcare_flask_app/app/static`
        (Verifique se o caminho `app/static` corresponde à estrutura do seu projeto).
*   Se o seu projeto usa uma pasta `templates` diretamente na raiz do projeto (e não dentro de `app/`), você pode não precisar configurar um mapeamento para templates, pois o Flask geralmente os encontra por padrão se estiverem em uma pasta chamada `templates` no mesmo nível do seu `run.py` ou dentro da pasta `app`.

**7. Recarregue sua Aplicação Web:**

*   No topo da aba "**Web**", clique no grande botão verde "**Reload seu_usuario_pythonanywhere.pythonanywhere.com**".

**8. Teste sua Aplicação:**

*   Abra o link `http://seu_usuario_pythonanywhere.pythonanywhere.com` em um navegador.
*   Verifique se o site carrega e se as funcionalidades principais estão operando.

**Possíveis Problemas e Dicas:**

*   **Error Log:** Se algo der errado, o primeiro lugar para procurar é o "**Error log**" na aba "Web". Ele geralmente dá pistas sobre o que aconteceu.
*   **Server Log:** O "**Server log**" também pode conter informações úteis.
*   **Caminhos:** A maioria dos erros no PythonAnywhere está relacionada a caminhos incorretos no arquivo WSGI ou nas configurações de arquivos estáticos. Verifique-os com atenção!
*   **Versão do Python:** Certifique-se de que a versão do Python selecionada para a web app é compatível com o seu código e as dependências.
*   **Database:** Se seu projeto usa um banco de dados SQLite, o arquivo do banco de dados (por exemplo, `site.db`) deve ser enviado junto com seu projeto e o caminho para ele no seu código Flask (em `config.py` ou similar) deve ser um caminho absoluto no PythonAnywhere, por exemplo: `SQLALCHEMY_DATABASE_URI = 'sqlite:////home/SEU_NOME_DE_USUARIO/techcare_flask_app/data/app.db'` (ajuste conforme a localização real do seu .db).

---

Por favor, siga estes passos com calma. Se encontrar qualquer dificuldade ou mensagem de erro, me diga exatamente qual é a mensagem e em qual passo você está, que tentarei te ajudar a solucionar!

Boa sorte com o deploy! 😊

