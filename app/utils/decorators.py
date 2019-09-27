# coding=utf-8

from functools import wraps, update_wrapper
from app.utils.redis import redis
import time

try:
    from flask import request, jsonify, g, make_response, current_app, abort
except:
    pass


def get_session():
    from app.account.models import ApiToken
    from app.auth.models import Session

    session = None
    if 'auth-token' in request.headers:
        session = Session.find_by_token(request.headers.get('auth-token'))
        if session is None:
            abort(401, {'code': 401, 'error': 'Unable to find account. Please provide a valid "auth-token" header.'})

    elif request.authorization is not None and 'password' in request.authorization:
        session = ApiToken.first(token=request.authorization.password, deleted=None)
        if session is None:
            abort(401, {'code': 401, 'error': 'Unable to find account. Please provide a valid API key in the password field of the basic auth.'})

    if session is not None:
        return session.account

    return None


class RateLimit(object):
    def __init__(self, key_prefix, limit, per=60):
        """
        key_prefix : Prefix of the key
        limit : Limit of request per "per" value
        per : Time for the limit, in seconds
        """
        self.reset = (int(time.time()) // per) * per + per
        self.key = key_prefix + str(self.reset)
        self.limit = limit
        self.per = per

        redis.add(self.key, 0, expire=per)
        counter = redis.incr(self.key)

        self.current = min(counter, limit)

    remaining = property(lambda x: x.limit - x.current)
    over_limit = property(lambda x: x.current >= x.limit)


def ratelimit(limit=150, per=60, add_global=True):  # 150 queries per 60 seconds by default
    def decorator(f):
        def rate_limited(*args, **kwargs):
            if not current_app.config['TESTING']:
                key = 'rate-limit/{0}/{1}'.format(request.endpoint, request.remote_addr)
                rlimit = RateLimit(key, limit, per)

                if add_global:
                    g._view_rate_limit = rlimit

                if rlimit.over_limit:
                    return make_response(jsonify({
                        'code': 429,
                        'error': 'Too many requests in the allowed time frame ({0} requests per {1} seconds).'.format(limit, per),
                        'remaining': 0,
                        'limit': rlimit.limit,
                        'reset': rlimit.reset
                    }), 429)

            return f(*args, **kwargs)

        return update_wrapper(rate_limited, f)

    return decorator


def authenticated(view_func):
    def _decorator(*args, **kwargs):
        account = get_session()

        if account is not None:
            g.account = account
            return view_func(*args, **kwargs)

        return make_response(jsonify({'code': 401, 'error': 'Unable to find account. Please provide a valid "api-token" header.'}), 401)

    return wraps(view_func)(ratelimit(120)(_decorator))
