# -*- config:utf-8 -*-
from app.utils.forms import BaseForm
from app.database import db
from sqlalchemy import Column, DateTime, func, Integer
import sqlalchemy.types as types
import datetime, json

from werkzeug.datastructures import ImmutableMultiDict


class JsonSerializable(object):
    __jsonserialize__ = ['id', ('__repr__', 'display')]
    UNIX_EPOCH = datetime.datetime(1970, 1, 1, 0, 0)

    def simple_serializer(self, item):
        if hasattr(item, 'to_json'):
            return getattr(item, 'to_json')()

        return {'id': item.id, 'display': item.__repr__()}

    def to_json(self, columns=None):
        if not columns:
            if hasattr(self.__jsonserialize__, '__call__'):
                return self.__jsonserialize__()

            columns = self.__jsonserialize__

        json = {}

        for column in columns:
            key = column

            if isinstance(column, tuple):
                key = column[1]
                column = column[0]

            prop = None
            if column.find('.') != -1:
                parts = column.split('.')
                prop = self
                for part in parts:
                    if not prop:
                        break
                    prop = getattr(prop, part, None)
            else:
                prop = getattr(self, column, None)

            if hasattr(prop, '__call__'):
                # In case we want to serialize a method
                if key[0:4] == 'get_':
                    key = key[4:]

                json[key] = prop()
            elif isinstance(prop, db.Model):
                # if a model, we simple serialize it
                json[key] = self.simple_serializer(prop)

            elif isinstance(prop, list):
                # Can be a list of direct item, or a list from a m2m
                # If it's a direct item, we go for it
                # If it's a m2m, we get the details of the related object
                json[key] = []
                for item in prop:
                    json[key].append(self.simple_serializer(item))

            elif isinstance(prop, datetime.datetime):
                # In case of a date, we output a timestamp
                json[key] = int((prop - self.UNIX_EPOCH).total_seconds() * 1000)
            elif isinstance(prop, datetime.date):
                # In case of a date, we output a timestamp
                json[key] = int((datetime.datetime.combine(prop, datetime.datetime.min.time()) - self.UNIX_EPOCH).total_seconds() * 1000)
            else:
                json[key] = prop

        return json

    def _map_object(json, key, value):
        if key.find('.') == -1:
            json[key] = value
        else:
            parts = key.split('.')
            current = json
            for part in parts:
                if not current[part]:
                    current[part] = {}


class BaseModel(db.Model, JsonSerializable):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=func.now())
    updated = Column(DateTime, onupdate=func.now())
    deleted = Column(DateTime)

    @classmethod
    def create(cls, form=None, **kwargs):
        if form:
            if not isinstance(form, BaseForm):
                raise Exception("Given form \"{0}\" in Model must be an instance of utils.forms.BaseForm".format(form.__class__.__name__))

            kwargs = form.get_as_dict()

        instance = cls()
        for key in kwargs:
            method = getattr(instance, 'set_{0}'.format(key), None)
            if method and callable(method):
                method(kwargs[key])
            else:
                setattr(instance, key, kwargs[key])

        return instance

    def update(self, form=None, save=False, **kwargs):
        if form:
            if not isinstance(form, BaseForm):
                raise Exception("Given form \"{0}\" in Model must be an instance of utils.forms.BaseForm".format(form.__class__.__name__))

            kwargs = form.get_as_dict()

        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)

        if save:
            self.save()

        return self

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        db.session.delete(self)
        if commit:
            return db.session.commit()

        return True

    @classmethod
    def _query(cls, params, _ignore=()):
        query = cls.query
        for key in params:
            if key in _ignore:
                continue
            if key in ('order_by', 'limit', 'page'):
                continue

            query = query.filter(getattr(cls, key) == params[key])

        order_by = None
        order_way = 'asc'

        if 'order_by' not in _ignore and 'order_by' in params:
            order_by = params['order_by']
            if params['order_by'][0:1] == '-':
                order_way = 'desc'
                order_by = params['order_by'][1:]
            params.pop('order_by', None)

        if order_by:
            query = query.order_by(getattr(getattr(cls, order_by), order_way)())

        return query

    @classmethod
    def find_all(cls, **kwargs):
        return cls._query(kwargs).all()

    @classmethod
    def first(cls, **kwargs):
        return cls._query(kwargs).first()

    @classmethod
    def find_by_request(cls, args, paginate=True):
        if isinstance(args, ImmutableMultiDict):
            data = dict((key, args.getlist(key) if len(args.getlist(key)) > 1 else args.getlist(key)[0]) for key in args.keys())
        else:
            data = args

        query = cls._query(data)

        if paginate:
            return cls.paginate(query, data)
        else:
            return ModelResponse(query.all())

    @classmethod
    def paginate(cls, query, params):
        if 'limit' not in params:
            params['limit'] = 25
        else:
            params['limit'] = int(params['limit'])
            if params['limit'] > 100:
                params['limit'] = 100
            elif params['limit'] < 1:
                params['limit'] = 1

        if 'page' not in params:
            params['page'] = 1
        else:
            params['page'] = int(params['page'])
            if params['page'] < 1:
                params['page'] = 1

        result = query.paginate(params['page'], params['limit'])
        return ModelResponse(items=result.items, **{
            'has_next': result.has_next,
            'has_prev': result.has_prev,
            'page': result.page,
            'pages': result.pages,
            'total': result.total
        })

    @classmethod
    def count(cls, query):
        count_q = query.statement.with_only_columns([func.count()]).order_by(None)
        return query.session.execute(count_q).scalar()


class ModelResponse(object):
    def __init__(self, items, **kwargs):
        self._items = items

        for key in kwargs:
            setattr(self, key, kwargs[key])

    def serialize(self, mapping):
        self.result = [i.to_json(mapping) for i in self._items]
        serialized = self.__dict__
        del (serialized['_items'])
        return serialized

    def __iter__(self):
        for item in self._items:
            yield item


class DbAmount(types.TypeDecorator):
    impl = types.Integer

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(types.Integer)

    def process_bind_param(self, value, dialect):
        if not value:
            return None

        return float(value) * 1000

    def process_result_value(self, value, dialect):
        if not value:
            return 0

        result = "{0:.2f}".format(float(value) / 1000)
        if result[-3:] == '.00':
            return result[0:-3]

        return result


class DbJson(types.TypeDecorator):
    impl = types.String

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(types.String)

    def process_bind_param(self, value, dialect):
        if not value:
            return None

        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if not value:
            return 0

        return json.loads(value)
