from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import logging
import os

load_dotenv()

db = SQLAlchemy()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(test_config=None):
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    database_url = os.getenv('DATABASE_URL', '')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if test_config:
        app.config.update(test_config)

    CORS(app)
    db.init_app(app)

    from .routes import api
    app.register_blueprint(api, url_prefix='/api')

    @app.route('/')
    def index():
        return render_template('index.html')

    with app.app_context():
        db.create_all()
        logger.info('Database tables created')

    logger.info('Application started')
    return app