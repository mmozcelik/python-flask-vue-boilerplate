import os, logging

APPLICATION_PATH = os.path.dirname(os.path.abspath(__file__))
ERROR_404_HELP = False

SECRET_KEY = os.getenv('APP_SECRET', 'secret key')

SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'mysql+pymysql://dbuser:12345678@localhost:3306/db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

DOC_USERNAME = 'api'
DOC_PASSWORD = 'password'
LAMBDA = False
if os.environ.get('DEPLOYMENT', None) == 'lambda':
    LAMBDA = True

ENV = os.environ.get('ENV', 'development')
DEBUG = False
TESTING = False
if ENV == 'development':
    DEBUG = True
elif ENV == 'testing':
    TESTING = True

REGION = 'us-east-1'
if ENV == 'production':
    REGION = 'us-east-2'

API_VERSION = 'v1'

BLUEPRINTS = ['account', 'auth']
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', None)

# Email related settings
MAILER_SERVICE = os.environ.get('MAILER_SERVICE', 'Sendgrid')
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', None)
CONTACT_NAME = 'MyApp'
CONTACT_EMAIL = 'support@myapp.com'

CACHE_URL = os.environ.get('CACHE_URL', 'redis://localhost:6379')
SQS_QUEUE_URL = os.environ.get('SQS_QUEUE_URL', None)

FRONTEND_BASE_URL = os.environ.get('FRONTEND_BASE_URL', 'localhost:8080')

ENABLE_INTERNAL_API_DOC = {'doc': 'Simple Dev Doc'} if ENV == 'development' else False
STRIPE_PRIVATE_KEY = os.environ.get('STRIPE_PRIVATE_KEY', None)

if MAILER_SERVICE == 'Sendgrid' and not SENDGRID_API_KEY:
    logging.error('Failed to setup sendgrid, please make sure env has SENDGRID_API_KEY setup.')
    raise 'Runtime'
