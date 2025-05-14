from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired

class MachineDiagnosticForm(FlaskForm):
    """Formulário para diagnóstico de máquina."""
    check_cpu = BooleanField('Verificar uso de CPU', default=True)
    check_memory = BooleanField('Verificar uso de memória', default=True)
    check_disk = BooleanField('Verificar saúde do disco', default=True)
    check_network = BooleanField('Verificar status de rede', default=True)
    submit = SubmitField('Realizar Diagnóstico')
