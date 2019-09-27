# coding:utf-8

from app.utils.models import JsonSerializable
from app.utils.redis import redis
from app.utils.mailers import get_mailer
from app.account.models import Account
import datetime, uuid, config


# Session data is kept in two cache entries one is session:account:<account_id> => <token>, session:token:<token> => <account_id>
class Session(JsonSerializable):
    __jsonserialize__ = ['token', 'expires', 'account']

    token = None
    account = None

    def __repr__(self):
        return self.token

    def __init__(self, account):
        self.account = account

        # Generate new session content for the account
        self.token = str(uuid.uuid4()).replace('-', '')

    def save(self):
        self.delete_old()

        account_key = self.get_account_key()

        pipe = redis.pipeline()
        pipe.setex(self.get_session_token_key(), 2 * 3600, self.account.id)
        pipe.setex(account_key, 2 * 3600, self.token)
        pipe.execute()

    def send(self):
        redis.set(self.get_account_key(), self.token, expire=24 * 3600)
        msg = get_mailer()("Here's your one-time login valid for 24 hours", template='accounts/reset')

        params = self.to_json([('account.__repr__', 'name'), ('account.email', 'email'), 'token'])
        params['urlb'] = '{0}/auth/token/{1}'.format(config.get('FRONTEND_BASE_URL'), self.token)
        msg.send_to(self.account.__repr__(), self.account.email, params)

    def get_session_token_key(self):
        return self._get_session_token_key(self.token)

    def get_account_key(self):
        return self._get_account_key(self.account.id)

    def delete_old(self):
        account_key = self._get_account_key(self.account.id)

        # Remove existing session
        existing_token = redis.get(account_key)
        if existing_token:
            pipe = redis.pipeline()
            pipe.delete(account_key)
            pipe.delete(self._get_session_token_key(existing_token))
            pipe.execute()

    @classmethod
    def delete_old_by_id(cls, account_id):
        account_key = cls._get_account_key(account_id)

        # Remove existing session
        existing_token = redis.get(account_key)
        if existing_token:
            pipe = redis.pipeline()
            pipe.delete(account_key)
            pipe.delete(cls._get_session_token_key(existing_token))
            pipe.execute()

    @classmethod
    def find_by_token(cls, token):
        session = None
        token_key = cls._get_session_token_key(token)
        if token_key:
            account_id = redis.get(token_key)

            if account_id:
                session = Session(Account.first(id=account_id))

        return session

    @classmethod
    def _get_account_key(cls, account_id):
        return 'session:account:{0}'.format(account_id)

    @classmethod
    def _get_session_token_key(cls, token):
        return 'session:token:{0}'.format(token)
