# -*- coding:utf-8 -*-

from app.database import db
from sqlalchemy import text

from app.utils.frequests import frequests
from app.account.models import Account
from cron_handler import delete_boto


def process(account_id):

    account = db.engine.execute(text('SELECT organization_id, email FROM accounts WHERE id = :account LIMIT 1'), account=account_id).first()
    if account is None:
        return None

    organization_id = account[0]
    account_email = account[1]

    frequests.delete(
        'https://api.sendinblue.com/v2.0/user/{0}'.format(account_email),
        headers={
            'api-key': Settings.get('SENDINBLUE_API_KEY')
        }
    )

    member = db.engine.execute(text("SELECT id FROM accounts WHERE is_admin = 1 AND organization_id = :organization AND id != :account LIMIT 1"), organization=organization_id, account=account_id).first()
    single_member = True if member is None else False

    account_entity = Account.first(email=account_email)
    if account_entity.admin and single_member:
        account_entity.organization.cancel_plan()

    db.engine.execute(text('DELETE FROM api_tokens WHERE account_id = :account'), account=account_id)
    db.engine.execute(text('DELETE FROM sessions WHERE account_id = :account'), account=account_id)
    db.engine.execute(text('DELETE FROM account_emails_verification WHERE email = :email'), email=account_email)

    if single_member:
        db.engine.execute(text('DELETE FROM contact_has_lists WHERE contact_id IN (SELECT id FROM contacts WHERE owner_id = :account)'), account=account_id)
        db.engine.execute(text('DELETE FROM contact_histories WHERE contact_id IN (SELECT id FROM contacts WHERE owner_id = :account)'), account=account_id)
        db.engine.execute(text('DELETE FROM contact_messages WHERE contact_id IN (SELECT id FROM contacts WHERE owner_id = :account)'), account=account_id)

        try:
            delete_boto("SELECT filepath FROM massive_imports WHERE account_id = " + str(account_id))
        except:
            pass
        db.engine.execute(text('DELETE FROM massive_imports WHERE account_id = :account'), account=account_id)

        delete_boto("SELECT filepath FROM message_attachments WHERE message_id IN (SELECT id FROM messages WHERE organization_id = " + str(organization_id) + ")")
        db.engine.execute(text('DELETE FROM message_attachments WHERE message_id IN (SELECT id FROM messages WHERE organization_id = :organization)'), organization=organization_id)
        db.engine.execute(text('DELETE FROM message_events WHERE message_id IN (SELECT id FROM messages WHERE organization_id = :organization)'), organization=organization_id)
        db.engine.execute(text('DELETE FROM messages WHERE organization_id = :organization'), organization=organization_id)

        db.engine.execute(text('DELETE FROM organization_emails WHERE organization_id = :organization'), organization=organization_id)
        db.engine.execute(text('DELETE FROM credits WHERE organization_id = :organization'), organization=organization_id)
        db.engine.execute(text('DELETE FROM lists WHERE organization_id = :organization'), organization=organization_id)

        db.engine.execute(text('DELETE FROM contacts WHERE owner_id = :account'), account=account_id)
        db.engine.execute(text('UPDATE organizations SET plan_id = NULL, next_payment = NULL, cc_expires = NULL, is_yearly = 0 WHERE id = :organization LIMIT 1'), organization=organization_id)
        # On ne supprime pas les payments, l'organizations et le compte
    else:
        new_account = long(member[0])

        db.engine.execute(text('DELETE FROM contact_histories WHERE owner_id = :account'), account=account_id)
        db.engine.execute(text('DELETE FROM contact_messages WHERE contact_id IN (SELECT id FROM contacts WHERE owner_id = :account)'), account=account_id)
        db.engine.execute(text('UPDATE contacts SET owner_id = :newowner WHERE owner_id = :account'), account=account_id, newowner=new_account)

    db.engine.execute(text('UPDATE accounts SET password = NULL, removed = UTC_DATE(), is_newsletter = 0 WHERE id = :account LIMIT 1'), account=account_id)

    return True
