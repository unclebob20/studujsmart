from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from redis import Redis
from config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
redis_client = None


def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Redis connection
    global redis_client
    redis_client = Redis.from_url(app.config['REDIS_URL'])

    # Login manager settings
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Prosím, prihláste sa pre prístup k tejto stránke.'

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.test import test_bp
    from app.routes.api import api_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(test_bp, url_prefix='/test')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Import all models to ensure they're registered with SQLAlchemy
    from app.models.user import User, UserSubject
    from app.models.subscription import Subscription, UsageLimit
    from app.models.subject import Subject, Topic, UserTopicProgress
    from app.models.question import QuestionTemplate, Question
    from app.models.test import TestSession, UserAnswer
    from app.models.gamification import Badge, UserBadge

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app