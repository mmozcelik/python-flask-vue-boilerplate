import sys, config, logging
from logging.handlers import RotatingFileHandler

from flask import Flask, jsonify, make_response, g


class Factory:

    def __init__(self):
        self.flask = None

    def set_flask(self, **kwargs):
        self.flask = Flask(__name__, **kwargs)
        self.flask.config.from_object(config)
        # setup logging
        file_handler = RotatingFileHandler('api.log', maxBytes=10000, backupCount=1)
        file_handler.setLevel(logging.INFO)
        self.flask.logger.addHandler(file_handler)
        stdout = logging.StreamHandler(sys.stdout)
        stdout.setLevel(logging.DEBUG)
        self.flask.logger.addHandler(stdout)

        configure_error_handlers(self.flask)
        configure_views(self.flask)
        configure_before_after_request(self.flask)

        return self.flask

    def set_db(self):
        from app.database import db
        db.init_app(self.flask)

    def set_migration(self):
        from app.database import db, migrate
        migrate.init_app(self.flask, db)

    def set_api(self):
        for namespace in self.flask.config['BLUEPRINTS']:
            blueprint = self.import_variable(namespace, 'views', 'app')

            args = {'url_prefix': '/' + self.flask.config['API_VERSION'] + '/' + blueprint.name}
            self.flask.register_blueprint(blueprint, **args)

    def import_variable(self, blueprint_path, module, variable_name):
        path = 'app.' + '.'.join(blueprint_path.split('.') + [module])
        mod = __import__(path, fromlist=[variable_name])
        return getattr(mod, variable_name)


def configure_error_handlers(app):
    @app.errorhandler(401)
    def authorization_required(e):
        return make_response(jsonify({'error': 'Authorization required. Your API Key does not appear to be valid.', 'code': 401}), 401)

    @app.errorhandler(403)
    def access_forbidden(e):
        return make_response(jsonify({'error': 'Access Forbidden.', 'code': 403}), 403)

    @app.errorhandler(404)
    def page_not_found(e):
        return make_response(jsonify({'error': 'Page not found.', 'code': 404}), 404)

    @app.errorhandler(405)
    def method_not_allowed(e):
        return make_response(jsonify({'error': 'Method not allowed.', 'code': 405}), 405)

    @app.errorhandler(410)
    def request_gone(e):
        return make_response(jsonify({'error': 'Gone.', 'code': 410}), 410)

    if app.debug:
        logging.info("DISABLING error handlers for this instance. (DEBUG mode ON)")
        return

    @app.errorhandler(500)
    @app.errorhandler(Exception)
    def internal_server_error(e):
        if isinstance(e, Exception):
            try:
                logging.exception(e)
            except:
                pass

        return make_response(jsonify({'error': 'Internal server error. We were notified!', 'code': 500}), 500)


def configure_before_after_request(app):
    @app.after_request
    def after_request_cors(response):
        """ Implementing CORS """
        h = response.headers
        h.add('Access-Control-Allow-Origin', '*')
        h.add('Access-Control-Allow-Methods', 'HEAD, GET, POST, PUT, DELETE, OPTIONS')
        h.add('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Host, Auth-Token, Authorization')

        return response

    @app.after_request
    def inject_x_rate_headers(response):
        limit = getattr(g, '_view_rate_limit', None)
        if limit:
            h = response.headers
            h.add('X-RateLimit-Remaining', str(limit.remaining))
            h.add('X-RateLimit-Limit', str(limit.limit))
            h.add('X-RateLimit-Reset', str(limit.reset))

        return response


def configure_views(app):
    """Add some simple views here like index_view"""
    from flask import send_from_directory

    @app.route("/")
    def redirect_to_web_app():
        # return redirect("/{0}/".format(current_app.config['API_VERSION']), code=301)
        return send_from_directory('templates', 'index.html')

    @app.route("/v1/")
    def show_documentation():
        return send_from_directory('../documentation', 'index.html')

    # for rule in app.url_map.iter_rules():
    #    print rule
    pass
