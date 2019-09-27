# coding:utf-8

from app.utils.forms import BaseForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, validators

from .models import Account, DisposableDomain
from app.utils.tools import check_domain_mx


class AccountCreateForm(BaseForm):
    name = StringField(validators=[validators.DataRequired(), validators.Length(min=3, max=100)], filters=[lambda x: x or None])
    email = StringField(validators=[validators.DataRequired(), validators.Email()], filters=[lambda x: x or None])
    password = PasswordField(validators=[validators.DataRequired()], filters=[lambda x: x or None])
    language = SelectField(choices=[("en", "English"), ], default="en", validators=[validators.Optional()], filters=[lambda x: x or None])
    token = StringField(validators=[validators.Optional(), ], filters=[lambda x: x or None])
    optin = BooleanField(false_values=['false', 'False', '0'], validators=[validators.Optional()], filters=[lambda x: x or False])
    captcha = StringField(validators=[validators.DataRequired(), ], filters=[lambda x: x or None])

    def validate_email(form, field):
        if Account.first(email=form.email.data, deleted=None):
            raise validators.ValidationError('There\'s already an account for this email address on Myapp.')

        email_domain = form.email.data[form.email.data.find('@') + 1:]
        if form.token.data is None:
            """
            We only refuse disposable if it's a new user
            When invited (token not None), we allow all kind
            """
            if email_domain in ['corporate.com', 'webmail.com', 'webmails.com']:
                raise validators.ValidationError('Disposable webmails like "{0}" are not allowed'.format(email_domain))

            if DisposableDomain.exists(email_domain):
                raise validators.ValidationError('Disposable webmails like "{0}" are not allowed'.format(email_domain))

        if check_domain_mx(email_domain) is False:
            raise validators.ValidationError('The domain does not seem to exist.')


class AccountUpdateForm(BaseForm):
    name = StringField(validators=[validators.Optional(), validators.Length(min=3, max=100)], filters=[lambda x: x or None])
    email = StringField(validators=[validators.Optional(), validators.Email()], filters=[lambda x: x or None])
    password = PasswordField(validators=[validators.Optional()], filters=[lambda x: x or None])
    language = SelectField(choices=[("en", "English"), ], default="en", validators=[validators.Optional()], filters=[lambda x: x or None])
    deleted = BooleanField(false_values=['false', 'False', '0'], validators=[validators.Optional()], filters=[lambda x: x or False])
    optin = BooleanField(false_values=['false', 'False', '0'], validators=[validators.Optional()], filters=[lambda x: x or False])


class AccountBillingForm(BaseForm):
    address = StringField(validators=[validators.Optional(), ], filters=[lambda x: x or None])
    zipcode = StringField(validators=[validators.DataRequired(), ], filters=[lambda x: x or None])
    city = StringField(validators=[validators.DataRequired(), ], filters=[lambda x: x or None])
    country = StringField(validators=[validators.DataRequired(), ], filters=[lambda x: x or None])
    company_name = StringField(validators=[validators.Optional(), ], filters=[lambda x: x or None])
    phone_number = StringField(validators=[validators.Optional(), ], filters=[lambda x: x or None])
