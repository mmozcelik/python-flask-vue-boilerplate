# -*- coding:utf-8 -*-

import urllib, json, requests
from requests_threads import AsyncSession

import urllib.parse as urlparse
from urllib.parse import urlencode

session = None


class Frequests(object):
    def __init__(self):
        global session
        if not session:
            session = AsyncSession(n=100)

    @classmethod
    def _call(cls, url, method, **kwargs):
        if 'headers' not in kwargs:
            kwargs['headers'] = {}

        if 'auth' in kwargs:
            kwargs['headers']['Authorization'] = 'Basic {0}'.format(
                '{0}:{1}'.format(kwargs['auth'][0], kwargs['auth'][1]).encode('base64').replace("\n", "")
            )

        if 'params' in kwargs:
            # @see http://stackoverflow.com/a/2506477/330867
            url_parts = list(urlparse.urlparse(url))
            query = dict(urlparse.parse_qsl(url_parts[4]))
            query.update(kwargs['params'])

            url_parts[4] = urlencode(query)

            url = urlparse.urlunparse(url_parts)

        payload = None
        if 'data' in kwargs:
            kwargs['headers']['Content-Type'] = 'application/x-www-form-urlencoded'
            payload = kwargs['data']

        if 'json' in kwargs:
            kwargs['headers']['Content-Type'] = 'application/json'
            kwargs['headers']['Accept'] = 'application/json'
            payload = json.dumps(kwargs['json'])

        if 'timeout' not in kwargs:
            kwargs['timeout'] = 10

        timeout = int(kwargs['timeout'])
        if 'files' in kwargs:
            pass

        if kwargs.get('async', False) is False:
            if method == 'GET':
                response = requests.get(url, headers=kwargs['headers'], timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, headers=kwargs['headers'], data=payload, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, headers=kwargs['headers'], data=payload, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=kwargs['headers'], data=payload, timeout=timeout)
            return Response(response)
        else:
            if method == 'GET':
                response = session.get(url, headers=kwargs['headers'])
            elif method == 'POST':
                response = session.post(url, headers=kwargs['headers'], data=payload)
            elif method == 'PUT':
                response = session.put(url, headers=kwargs['headers'], data=payload)
            elif method == 'DELETE':
                response = session.delete(url, headers=kwargs['headers'], data=payload)

            return response

    @classmethod
    def get(cls, url, **kwargs):
        return cls._call(url, 'GET', **kwargs)

    @classmethod
    def post(cls, url, **kwargs):
        return cls._call(url, 'POST', **kwargs)

    @classmethod
    def put(cls, url, **kwargs):
        return cls._call(url, 'PUT', **kwargs)

    @classmethod
    def delete(cls, url, **kwargs):
        return cls._call(url, 'DELETE', **kwargs)


class Response(object):
    def __init__(self, fetched):
        self.status_code = None
        self.content = None
        self.fetched = fetched
        if fetched is not None:
            self.content = fetched.content
            self.status_code = fetched.status_code

    def json(self):
        if self.content is None:
            return None

        try:
            return json.loads(self.content)
        except:
            return None

    def raise_for_status(self):
        if str(self.status_code)[0:1] in ['4', '5']:
            raise FRequestException("{0} status code error".format(self.status_code), self.status_code, self.content)


class FRequestException(Exception):
    def __init__(self, value, status_code, content):
        self.value = value
        self.status_code = status_code
        self.content = content

    def __str__(self):
        return repr(self.value)

    def __repr__(self):
        return repr(self.value)
