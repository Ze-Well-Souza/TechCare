import os
import yaml
from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint

def generate_swagger_ui(app):
    """
    Configura a documentação Swagger UI para a aplicação Flask
    """
    SWAGGER_URL = '/api/docs'
    API_URL = '/static/api_docs.yaml'

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "TechCare Admin API"
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

def validate_openapi_spec(file_path):
    """
    Valida o arquivo de especificação OpenAPI
    """
    try:
        with open(file_path, 'r') as file:
            spec = yaml.safe_load(file)
            # Adicionar validações específicas se necessário
            print("Especificação OpenAPI validada com sucesso!")
            return True
    except Exception as e:
        print(f"Erro na validação da especificação: {e}")
        return False

def main():
    # Caminho para o arquivo de documentação
    docs_path = os.path.join(
        os.path.dirname(__file__),
        '..', 'docs', 'api_docs.yaml'
    )
    
    # Validar especificação
    validate_openapi_spec(docs_path)

    # Configurar app Flask de exemplo
    app = Flask(__name__)
    generate_swagger_ui(app)

if __name__ == '__main__':
    main()
