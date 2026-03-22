# app/routes/__init__.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ── Sécurité ──────────────────────────────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # ── Base de données (Neon PostgreSQL) ─────────────────
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '').replace(
        'postgres://', 'postgresql://'   # Correction pour SQLAlchemy
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_pre_ping': True,
    'pool_recycle': 280,
    'pool_size': 5,
    'max_overflow': 2,
    'connect_args': {
        'connect_timeout': 10,
        'keepalives': 1,
        'keepalives_idle': 30,
        'keepalives_interval': 5,
        'keepalives_count': 5,
    }
}


    # ── Cloudinary ────────────────────────────────────────
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY    = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')

    # ── Email ─────────────────────────────────────────────
    MAIL_SERVER         = os.environ.get('MAIL_SERVER', 'smtp-relay.brevo.com')
    MAIL_PORT           = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS        = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USE_SSL        = os.environ.get('MAIL_USE_SSL', 'False') == 'True'
    MAIL_USERNAME       = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD       = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'amgsbsfax@gmail.com')

    # ── Upload ────────────────────────────────────────────
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024   # 16 MB max
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf', 'pptx', 'ppt'}

    # ── Babel (i18n) ──────────────────────────────────────
    LANGUAGES      = ['fr', 'ar']
    BABEL_DEFAULT_LOCALE  = 'fr'
    BABEL_DEFAULT_TIMEZONE = 'Africa/Tunis'


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig,
}
