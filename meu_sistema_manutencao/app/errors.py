from flask import render_template, request, jsonify
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    """Registrar manipuladores de erro globais."""
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Manipulador para erro 404 - Página não encontrada."""
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify(error='Recurso não encontrado'), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        """Manipulador para erro 403 - Acesso negado."""
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify(error='Acesso negado'), 403
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_error(error):
        """Manipulador para erro 500 - Erro interno do servidor."""
        from . import db
        db.session.rollback()
        
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify(error='Erro interno do servidor'), 500
        return render_template('errors/500.html'), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        """Manipulador genérico para exceções não tratadas."""
        # Passar através de exceções HTTP
        if isinstance(e, HTTPException):
            return e

        # Registrar erro
        app.logger.error(f'Erro não tratado: {str(e)}', exc_info=True)
        
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify(error='Erro inesperado'), 500
        return render_template('errors/unexpected.html', error=str(e)), 500
