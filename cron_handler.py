# -*- coding:utf-8 -*-

import logging, os, sys, config

from app.database import db
from sqlalchemy import text

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(PROJECT_PATH, "app"))


def delete_boto(query):
    from app.utils import s3file

    items = db.engine.execute(text(query))
    for result in items:
        filepath = result[0]
        s3file.delete(filepath)


def cron_creditcard(event, context):
    from app.utils.mailers import get_mailer

    logging.info("cron: Running emails credit card")
    # Send email for organization that have their credit card that will expire
    emails = db.engine.execute(text(
        "SELECT a.name, a.email FROM accounts a LEFT JOIN organizations o ON o.id = a.organization_id WHERE a.is_admin = 1 AND cc_expires IS NOT NULL AND DATE_FORMAT(cc_expires, '%Y-%m') = DATE_FORMAT(UTC_DATE(), '%Y-%m') GROUP BY a.id"))
    for email in emails:
        msg = get_mailer()("Your credit card will expire", template='payments/creditcard_expire')
        params = {
            'name': email[0]
        }
        msg.send_to(email[0], email[1], params)

    return 'ok'
