from flask import Blueprint, render_template
from flask_login import login_required

diagnostic = Blueprint('diagnostic', __name__, url_prefix='/diagnostic')

@diagnostic.route('/')
@login_required
def index():
    """Rota principal de diagnóstico"""
    return render_template('diagnostic/index.html')

# Importa submódulos de rotas
from . import diagnostic_overview
from . import diagnostic_analysis
from . import diagnostic_api 