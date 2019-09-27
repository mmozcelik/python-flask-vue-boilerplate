from pymemcache.client.hash import HashClient
import elasticache_auto_discovery, os, config

if config.ENV == 'development':
    memcache = HashClient([('localhost', 11211)])
else:
    # for lambda deployment
    elasticache_config_endpoint = config.CACHE_URL
    nodes = elasticache_auto_discovery.discover(elasticache_config_endpoint)
    nodes = map(lambda x: (x[1], int(x[2])), nodes)
    memcache = HashClient(nodes)
