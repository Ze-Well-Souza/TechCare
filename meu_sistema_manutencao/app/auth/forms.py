from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
import re
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp
from ..models import User, PLANOS

def validate_password_complexity(form, field):
    '''Validar complexidade da senha.'''
    if not re.search(r'[A-Z]', field.data):
        raise ValidationError('Senha deve conter pelo menos uma letra maiúscula.')
    if not re.search(r'[a-z]', field.data):
        raise ValidationError('Senha deve conter pelo menos uma letra minúscula.')
    if not re.search(r'\d', field.data):
        raise ValidationError('Senha deve conter pelo menos um número.')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', field.data):
        raise ValidationError('Senha deve conter pelo menos um caractere especial.')

class LoginForm(FlaskForm):
    email = StringField('Email', 
        validators=[
            DataRequired(message='Email é obrigatório'), 
            Email(message='Email inválido'),
            Regexp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', 
                   message='Formato de email inválido')
        ])
    password = PasswordField('Senha', 
        validators=[
            DataRequired(message='Senha é obrigatória'), 
            Length(min=8, max=32, message='Senha deve ter entre 8 e 32 caracteres'),
            validate_password_complexity
        ])
    remember_me = BooleanField('Manter conectado')
    submit = SubmitField('Entrar')

    def validate(self, extra_validators=None):
        '''Validação adicional do formulário.'''
        if not super().validate(extra_validators):
            return False
        
        # Validação extra de email
        if not self.email.data.lower().replace(' ', ''):
            self.email.errors.append('Email não pode ser vazio ou conter apenas espaços')
            return False
        
        return True

class RegistrationForm(FlaskForm):
    nome = StringField('Nome Completo', 
        validators=[
            DataRequired(message='Nome é obrigatório'), 
            Length(min=3, max=100, message='Nome deve ter entre 3 e 100 caracteres')
        ])
    email = StringField('Email', 
        validators=[
            DataRequired(message='Email é obrigatório'), 
            Email(message='Email inválido')
        ])
    password = PasswordField('Senha', 
        validators=[
            DataRequired(message='Senha é obrigatória'), 
            Length(min=6, message='Senha deve ter no mínimo 6 caracteres')
        ])
    confirm_password = PasswordField('Confirmar Senha', 
        validators=[
            DataRequired(message='Confirmação de senha é obrigatória'),
            EqualTo('password', message='Senhas não conferem')
        ])
    plano = SelectField('Plano', 
        choices=[(plano, PLANOS[plano]['nome']) for plano in PLANOS.keys()],
        validators=[DataRequired(message='Selecione um plano')])
    is_admin = BooleanField('Administrador')
    submit = SubmitField('Registrar')

    def validate_email(self, email):
        """Validar se email já existe."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email já cadastrado.')
