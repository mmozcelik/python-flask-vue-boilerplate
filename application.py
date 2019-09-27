'''
Simple Flask application to test deployment to Amazon Web Services
Uses Elastic Beanstalk and RDS
Author: Scott Rodkey - rodkeyscott@gmail.com
Step-by-step tutorial: https://medium.com/@rodkey/deploying-a-flask-application-on-aws-a72daba6bb80
'''

from wsgi import app
import logging

if __name__ == '__main__':
    app.run(host='0.0.0.0')
else:
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handler = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
