import datetime
import uuid
import config

from flask import g
from sqlalchemy.orm import relationship, backref

from app.utils import BCrypt, capitalize_all
from app.utils.mailers import get_mailer
from app.utils.models import BaseModel
from ..database import db


class Account(BaseModel):
    __tablename__ = 'account'
    __jsonserialize__ = [('__repr__', 'name'), ('get_firstname', 'firstname'), 'email', 'verified', 'created', 'optin']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=True, unique=True, index=True)
    password = db.Column(db.String(250), nullable=True, default=None)
    original_ip = db.Column(db.String(15), nullable=False)

    referrer = db.Column(db.String(250), nullable=True, default=None)
    referrer_domain = db.Column(db.String(250), nullable=True, default=None)
    campaign = db.Column(db.String(250), nullable=True, default=None)

    language = db.Column(db.String(2), nullable=False, default='EN')
    verified = db.Column('is_verified', db.Boolean, nullable=False, default=False)
    optin = db.Column('is_optin', db.Boolean, nullable=False, default=True)

    stripe_customer_id = db.Column(db.String(250), nullable=True, default=None)
    subscription_id = db.Column(db.String(50), nullable=True)

    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), nullable=True)
    plan = relationship('Plan', backref=backref('account'))

    low_credits_reminder = db.Column('is_low_credits_reminder', db.Boolean, nullable=False, default=True)

    def __repr__(self):
        if not self.name:
            return capitalize_all(self.email[0:self.email.index('@')])

        return capitalize_all(self.name)

    def get_name(self):
        return self.__repr__()

    def get_firstname(self):
        full_name = self.__repr__()
        if full_name and full_name.find(' ') > -1:
            return full_name[0:full_name.index(' ')]

        return full_name

    def __init__(self, **kwargs):
        super(Account, self).__init__(**kwargs)

    def set_password(self, clear):
        self.password = BCrypt.hash(clear)

    def check_passwd(self, password):
        try:
            return BCrypt.hash(password, self.password) == self.password
        except ValueError:
            return False

    def get_api_token(self):
        token = ApiToken.first(account_id=self.id, deleted=None)
        if token:
            return token.token

        return None

    def to_fulljson(self):
        return self.to_json([('__repr__', 'name'), ('get_firstname', 'firstname'), 'email', 'verified', 'created', 'language', 'get_api_token', 'optin'])

    def get_session_data(self):
        from app.credit.models import Credit
        result = self.to_json()
        result['credits'] = Credit.get_details(self.id)

        return result


class ApiToken(BaseModel):
    __tablename__ = 'api_token'

    id = db.Column(db.Integer, primary_key=True)

    token = db.Column(db.String(250), nullable=False, unique=True, index=True)

    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    account = relationship('Account', backref=backref('tokens'))

    def __repr__(self):
        return self.token

    def __init__(self, account_id):
        self.account_id = account_id
        self.token = str(uuid.uuid4())

    @classmethod
    def disable_all(cls, account_id):
        result = cls.query.filter(cls.account_id == account_id).update({cls.deleted: datetime.datetime.utcnow()})
        db.session.commit()
        return result


class AccountEmailVerification(BaseModel):
    __tablename__ = 'account_email_verification'
    __jsonserialize__ = ['id', ('account.__repr__', 'name'), 'email']

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(250), nullable=False, index=True)

    credits = db.Column('is_credits', db.Boolean, nullable=False, default=False)
    token = db.Column(db.String(100), nullable=True, unique=True, index=True)

    account = relationship('Account', backref=backref('email_verifications'))
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)

    def __repr__(self):
        if self.account is not None:
            return self.account.get_name()

        return self.email

    def __init__(self, account=None, credits=False):
        self.token = str(uuid.uuid4()).replace('-', '')

        if account:
            self.email = account.email
            self.account_id = account.id
            self.account = account
        else:
            self.email = g.account.email
            self.account_id = g.account.id

        self.credits = credits

    def send(self, **kwargs):
        msg = get_mailer()("Please confirm your email address", template='accounts/email_validation_account')

        params = self.to_json(['email', ('__repr__', 'name'), 'token'])
        params['urlb'] = self.get_url()
        params.update(kwargs)
        return msg.send_to(params['name'], params['email'], params)

    def get_url(self):
        return '{0}/validate/token/{1}'.format(config.FRONTEND_BASE_URL, self.token)

    @classmethod
    def delete_by_account_id(cls, account_id):
        result = cls.query.filter(cls.account_id == account_id).delete()
        db.session.commit()
        return result

    @classmethod
    def find_by_token(cls, token):
        return cls.query.filter(cls.token == token).first()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter(cls.email == email).first()


# @see https://github.com/martenson/disposable-email-domains
class DisposableDomain(BaseModel):
    __tablename__ = 'disposable_domain'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False, unique=True, index=True)

    def __repr__(self):
        return self.name

    @classmethod
    def exists(cls, name):
        d = cls.query.filter(cls.name == name).first()
        return d is not None


class AccountBilling(BaseModel):
    __tablename__ = 'account_billing'
    __jsonserialize__ = ['id', 'company_name', 'address', 'zipcode', 'city', 'country', 'phone_number']

    id = db.Column(db.Integer, primary_key=True)

    company_name = db.Column(db.String(250), nullable=True)
    address = db.Column(db.String(250), nullable=True)
    zipcode = db.Column(db.String(250), nullable=True)
    city = db.Column(db.String(250), nullable=True)
    country = db.Column(db.String(250), nullable=True)
    phone_number = db.Column(db.String(50), nullable=True)

    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=True)
    account = relationship('Account', backref=backref('billing'))

    def __repr__(self):
        if self.account is not None:
            return self.account.get_name()

        return self.email

    def __init__(self, account_id, email=None):
        self.account_id = account_id
        self.email = email

    @classmethod
    def find_by_account(cls, account_id):
        return cls.query.filter(cls.account_id == account_id).first()
