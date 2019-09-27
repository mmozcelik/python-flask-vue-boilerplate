import click
from werkzeug.middleware.proxy_fix import ProxyFix

from .factory import Factory


def create_app():
    f = Factory()
    f.set_flask()
    f.set_db()
    f.set_migration()
    f.set_api()

    # from models import Example

    app = f.flask

    if app.config['TESTING']:  # pragma: no cover
        # Setup app for testing
        @app.before_first_request
        def initialize_app():
            pass

    app.wsgi_app = ProxyFix(app.wsgi_app)

    @app.cli.command()
    @click.argument('command')
    def setup(command):
        pass

    return app
