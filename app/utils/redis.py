# -*- coding:utf-8 -*-

import redis as redis_cli
import config


class RedisClient:
    redis = None

    def __init__(self):
        self.redis = redis_cli.from_url(config.CACHE_URL)

    def set(self, key, value, expire=None, nx=False):
        self.redis.set(key, value, ex=expire, nx=nx)

    def get(self, key):
        return self.redis.get(key)

    def delete(self, key):
        return self.redis.delete(key)

    def incr(self, key, amount=1):
        return self.redis.incr(key, amount)

    def add(self, key, value, expire=None):
        self.redis.set(key, value, ex=expire, nx=True)

    def pipeline(self):
        return self.redis.pipeline()


redis = RedisClient()
