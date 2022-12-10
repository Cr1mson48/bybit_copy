from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired


class APIForm(FlaskForm):
    apiKey = StringField('apiKey', validators=[DataRequired()])
    secretKey = StringField('secretKey', validators=[DataRequired()])
    submit = SubmitField('Добавить')