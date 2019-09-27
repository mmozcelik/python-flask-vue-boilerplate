from flask_migrate import Migrate
import config

if config.LAMBDA:
    from app.utils.sqlalchemyutils import SQLAlchemy

    db = SQLAlchemy()
else:
    from flask_sqlalchemy import SQLAlchemy

    # Elastic Beanstalk initalization
    db = SQLAlchemy()

migrate = Migrate()
