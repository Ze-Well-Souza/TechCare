import requests

# URL da rota de limpeza (ajuste se necessário)
url = "http://127.0.0.1:5000/cleaner/execute_cleanup"

# Dados do formulário (opções de limpeza)
# Estas são as opções que o backend espera em request.form.getlist("cleanup_options")
data = {
    "cleanup_options": ["temp_system", "browser_cache", "recycle_bin"]
}

# Cookies de sessão (necessário se a rota for protegida por @login_required)
# Você precisaria obter o cookie de sessão após o login via navegador.
# Por enquanto, vamos tentar sem, mas pode falhar se o login for estritamente necessário
# e não houver uma sessão ativa para o requests.
# Para um teste mais robusto, o ideal seria modificar o JS do frontend para fazer a chamada real.

# Como alternativa, se o teste direto via script for complexo devido à autenticação,
# podemos modificar o JavaScript no template disk_cleanup.html para fazer uma chamada AJAX real.

# Tentativa de POST direto (pode falhar devido à falta de sessão de login)
# Em um ambiente de teste real, você precisaria de uma sessão logada.
# Para o agente, modificar o JS do frontend é uma abordagem mais integrada.

# Este script é mais para ilustrar como seria um POST direto.
# A melhor abordagem para o agente é modificar o JavaScript no HTML.

print(f"Simulando POST para {url} com dados: {data}")

# Como a rota é @login_required, uma chamada direta via requests sem cookies de sessão
# provavelmente resultará em um redirecionamento para a página de login ou um erro 401.
# Portanto, a modificação do JS no frontend é a estratégia mais viável para o agente.

print("Para testar efetivamente a rota POST /execute_cleanup, a melhor abordagem é modificar o JavaScript")
print("no arquivo app/templates/cleaner/disk_cleanup.html para que ele envie uma requisição AJAX real")
print("em vez de apenas simular a limpeza no frontend. Isso manterá o contexto da sessão de login.")

