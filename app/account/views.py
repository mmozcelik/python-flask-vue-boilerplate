from flask import g, jsonify, request, abort, make_response, Blueprint
from flask.views import MethodView

from .forms import AccountUpdateForm, AccountCreateForm, AccountBillingForm
from .models import Account, ApiToken, AccountEmailVerification, AccountBilling
from ..credit.models import Credit
from ..auth.models import Session

from app.utils.decorators import authenticated, ratelimit

from app.utils.taskqueue import send_task
import datetime, json, logging, config

from app.utils.frequests import Frequests
import urllib.parse as urlparse

from ..database import db
from sqlalchemy.exc import IntegrityError

app = Blueprint('internal/account', __name__)


class AccountWS(MethodView):
    @authenticated
    def get(self):
        logging.info("Returning result!")
        return jsonify(g.account.to_fulljson())

    @ratelimit(10)
    def post(self):
        logging.info("Creating a new account, reading sent form!")
        form = AccountCreateForm(request.form)
        if not form.validate():
            return form.errors_as_json()

        if config.ENV != 'development':
            captcha_result = Frequests.post(
                'https://www.google.com/recaptcha/api/siteverify',
                data={
                    'secret': '6LfBwbkUAAAAAMGaa6IJ1ZqWFzmrFfpjHYfMAEBF',
                    'response': form.captcha.data
                }
            )
            if not captcha_result.json()['success']:
                form.errors['email'] = ['Invalid captcha']
                return make_response(form.errors_as_json(), 400)

        remote_ip = request.remote_addr
        if request.access_route:
            # return remote ip
            remote_ip = request.access_route[0]

        account = Account.create(form)
        account.original_ip = remote_ip
        account.verified = False

        try:
            referrer = request.cookies.get('_referrer')
            userdata = json.loads(referrer.decode('base64'))

            account.referrer = userdata.get('referrer', None)
            account.referrer_domain = userdata.get('domain', None)
            account.partner = userdata.get('partner', None)
        except:
            pass

        logging.info("Saving account!")
        try:
            account.save()
            ApiToken(account.id).save()

            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            form.errors['email'] = ['There\'s already an account for this email address on Myapp.']
            return make_response(form.errors_as_json(), 400)

        send_task(queue_name='creation', params={
            'account_id': account.id
        })

        session = Session(account)
        session.save()
        logging.info("Completed account creation!")
        return jsonify(session.to_json())

    @authenticated
    def put(self):
        form = AccountUpdateForm(request.form)
        if not form.validate():
            return form.errors_as_json()

        if g.account.deleted:
            g.account.deleted = None
        else:
            if form.deleted.data:
                g.account.deleted = datetime.datetime.utcnow()
                g.account.save()

                return make_response('', 204)

            if form.email.data:
                email_account = Account.first(email=form.email.data, deleted=None)
                if email_account and email_account.id != g.account.id:
                    form.errors['email'] = ['This email is already in use.']
                    return form.errors_as_json(409)

            params = form.get_as_dict()
            del params['deleted']
            if 'password' in params:
                if params['password'] is not None:
                    g.account.set_password(params['password'])

                del params['password']

            g.account.update(**params)
        try:
            g.account.save()
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            form.errors['email'] = ['This email is already in use.']
            return make_response(form.errors_as_json(), 400)

        return jsonify(g.account.to_json())

    @authenticated
    def delete(self):
        passwd = request.form.get('password', None)
        if not g.account.check_passwd(passwd):
            abort(403)

        send_task(queue_name='delete', params={
            'account_id': g.account.id
        })

        return make_response('', 202)


app.add_url_rule('/', view_func=AccountWS.as_view('accounts'))


@app.route('/data', methods=['GET'])
@authenticated
def account_data():
    return jsonify(g.account.get_session_data())


@app.route('/referrer', methods=['POST'])
def account_referrer():
    response = make_response('', 202)
    if '_referrer' not in request.cookies:
        referrer = request.form.get('referrer', None)
        parsed = None
        if referrer is not None:
            parsed = urlparse(referrer)

        userdata = {
            'referrer': referrer,
            'domain': parsed.netloc if parsed is not None else None,
            'partner': request.form.get('partner', None)
        }

        response.set_cookie('_referrer', json.dumps(userdata).encode('base64'), expires=datetime.datetime.utcnow() + datetime.timedelta(days=31), max_age=60 * 60 * 24 * 31)

    return response


@app.route('/email/resend', methods=['POST'])
@authenticated
def account_resend():
    verification = AccountEmailVerification.find_by_email(g.account.email)
    if verification is None:
        verification = AccountEmailVerification(g.account, (not g.account.account_verified))
        verification.save()

    verification.send()

    return make_response('', 202)


@app.route('/email/validate', methods=['POST'])
def account_validate():
    account_email = AccountEmailVerification.find_by_token(request.form.get('token'))
    if not account_email:
        abort(404)

    account = account_email.account
    if account_email.credits:
        Credit(50, account=account_email.account).save()

    try:
        account.verified = True
        account.save()

        session = Session(account_email.account)
        session.save()

        AccountEmailVerification.delete_by_account_id(account_email.account_id)
        return jsonify(session.to_json())
    except:
        abort(500)


class AccountApiWS(MethodView):
    decorators = [authenticated]

    def get(self):
        token = ApiToken.first(account_id=g.account.id, deleted=None)

        return jsonify({
            'token': token.token if token is not None else None
        })

    def post(self):
        ApiToken.disable_all(g.account.id)
        token = ApiToken(g.account.id)
        token.save()

        return jsonify({
            'token': token.token
        })


app.add_url_rule('/api/', view_func=AccountApiWS.as_view('api'))


class AccountBillingWS(MethodView):
    decorators = [authenticated]

    def get(self):
        token = AccountBilling.first(account_id=g.account.id, deleted=None)

        return jsonify({
            'token': token.token if token is not None else None
        })

    def post(self):
        form = AccountBillingForm(request.form)
        if not form.validate():
            return form.errors_as_json()

        billing = AccountBilling.create(form)
        billing.save()

        return jsonify(billing.to_json())


app.add_url_rule('/billing/', view_func=AccountBillingWS.as_view('billing'))
