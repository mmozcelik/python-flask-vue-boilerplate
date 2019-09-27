# coding:utf-8

from app.utils.forms import BaseForm
from wtforms import StringField, PasswordField, validators


class AuthenticationForm(BaseForm):
    email = StringField(validators=[validators.DataRequired(), validators.Email()])
    password = PasswordField(validators=[validators.DataRequired()])


class LostPasswordForm(BaseForm):
    email = StringField(validators=[validators.DataRequired(), validators.Email()], filters=[lambda x: x or None])
