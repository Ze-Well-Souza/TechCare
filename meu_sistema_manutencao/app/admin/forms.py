from flask_wtf import FlaskForm
from wtforms import SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from ..models import PLANOS

class UserManagementForm(FlaskForm):
    """Formulário para gerenciamento de usuários pelo admin."""
    plano = SelectField('Plano', 
        choices=[(plano, PLANOS[plano]['nome']) for plano in PLANOS.keys()],
        validators=[DataRequired(message='Selecione um plano')])
    is_active = BooleanField('Usuário Ativo')
    submit = SubmitField('Atualizar Usuário')
