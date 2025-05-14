from flask_apispec import FlaskApiSpec
from apispec import APISpec
from apispec.ext.marshmallow import OpenAPIConverter

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "TechCare Admin Panel API",
        "description": "API para gerenciamento administrativo do sistema TechCare",
        "version": "1.0.0",
        "contact": {
            "name": "Equipe TechCare",
            "email": "suporte@techcare.com"
        }
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Insira o token JWT no formato: Bearer <token>"
        }
    },
    "security": [
        {
            "Bearer": []
        }
    ],
    "host": "api.techcare.com",
    "basePath": "/v1",
    "schemes": [
        "https"
    ],
    "consumes": [
        "application/json"
    ],
    "produces": [
        "application/json"
    ]
}

def configure_swagger(app):
    """Configura a documentação Swagger para a aplicação"""
    app.config.update({
        'APISPEC_SWAGGER_URL': '/swagger/',
        'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'
    })
    
    docs = FlaskApiSpec(app)
    
    spec = APISpec(
        title="TechCare Admin Panel API",
        version="1.0.0",
        openapi_version="2.0",
        plugins=[OpenAPIConverter()],
        info=swagger_template['info']
    )
    
    # Adiciona definições de segurança
    spec.components.security_scheme(
        'Bearer', 
        {
            'type': 'http', 
            'scheme': 'bearer', 
            'bearerFormat': 'JWT'
        }
    )
    
    return docs

def register_swagger_routes(app, docs):
    """Registra rotas para documentação Swagger"""
    @app.route('/docs')
    def swagger_docs():
        return app.send_static_file('swagger.json')
    
    @app.route('/swagger')
    def swagger_ui():
        return app.send_static_file('swagger-ui.html')

def generate_swagger_json(app):
    """Gera o arquivo JSON de especificação Swagger"""
    with app.test_request_context():
        spec = docs.spec.to_dict()
    
    import json
    with open('static/swagger.json', 'w') as f:
        json.dump(spec, f, indent=2)
