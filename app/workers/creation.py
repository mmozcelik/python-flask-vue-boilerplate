# -*- coding:utf-8 -*-

from app.account.models import Account, AccountEmailVerification


def process(account_id):
    account = Account.first(id=int(account_id))
    verification = AccountEmailVerification(account)
    verification.send()
