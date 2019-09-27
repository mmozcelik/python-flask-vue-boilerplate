# coding:utf-8

from flask import g, jsonify, make_response, Blueprint
from flask import request
from app.utils.decorators import authenticated, ratelimit

from .models import Session
from .forms import AuthenticationForm, LostPasswordForm
from app.account.models import Account

app = Blueprint('internal/auth', __name__)


@app.route('/login', methods=['POST'])
@ratelimit(60)
def login():
    form = AuthenticationForm(request.form)
    if not form.validate():
        return form.errors_as_json()

    account = Account.first(email=form.email.data, deleted=None)
    if not account or not account.check_passwd(form.password.data):
        form.errors['email'] = ['Invalid password or account does not exist.']
        return make_response(form.errors_as_json(), 400)

    if request.form.get('api', '0') == '1':
        return jsonify(account.to_fulljson())

    session = Session(account)
    session.save()

    result = session.to_json()
    result['account'] = account.get_session_data()
    return jsonify(result)


@app.route("/lost", methods=['POST'])
@ratelimit(60)
def lost_password_send():
    form = LostPasswordForm(request.form)
    if not form.validate():
        return form.errors_as_json()

    account = Account.first(email=form.email.data, deleted=None)
    if account:
        session = Session(account)
        session.save()
        try:
            session.send()
        except:
            form.errors['email'] = ['An error occurred, please try again.']
            return make_response(form.errors_as_json(), 400)

    return make_response('', 204)


@app.route('/logout', methods=['POST'])
@authenticated
def logout():
    Session(g.account).delete_old()
    return make_response('', 204)
