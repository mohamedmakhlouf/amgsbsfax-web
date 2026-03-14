# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_babel import Babel
import os

# Extensions
db      = SQLAlchemy()
migrate = Migrate()
login   = LoginManager()
babel   = Babel()

login.login_view    = 'admin.login'
login.login_message = 'Veuillez vous connecter pour accéder à cette page.'

def get_locale():
    from flask import session, request
    if 'lang' in session:
        return session['lang']
    return request.accept_languages.best_match(['fr', 'ar'], 'fr')

def create_app(config_name=None):
    app = Flask(__name__)

    # ── Configuration ─────────────────────────────────────
    from config import config
    env = config_name or os.environ.get('FLASK_ENV', 'default')
    cfg = config.get(env, config['default'])
    app.config.from_object(cfg)

    # ── Extensions ────────────────────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    # Flask-Mail ← ICI, à l'intérieur de create_app après app.config
    from app.utils.mail import mail
    mail.init_app(app)

    # Flask-Babel
    try:
        babel.init_app(app, locale_selector=get_locale)
    except TypeError:
        babel.init_app(app)
        babel.localeselector(get_locale)

    # ── Cloudinary (optionnel en dev) ─────────────────────
    cloud_name = app.config.get('CLOUDINARY_CLOUD_NAME', '')
    if cloud_name and cloud_name not in ('test', ''):
        import cloudinary
        cloudinary.config(
            cloud_name = cloud_name,
            api_key    = app.config.get('CLOUDINARY_API_KEY'),
            api_secret = app.config.get('CLOUDINARY_API_SECRET'),
            secure     = True
        )

    # ── Blueprints ────────────────────────────────────────
    from app.routes.main      import main_bp
    from app.routes.events    import events_bp
    from app.routes.register  import register_bp
    from app.routes.abstracts import abstracts_bp
    from app.routes.contact   import contact_bp
    from app.routes.admin     import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(events_bp,    url_prefix='/evenements')
    app.register_blueprint(register_bp,  url_prefix='/inscription')
    app.register_blueprint(abstracts_bp, url_prefix='/resumes')
    app.register_blueprint(contact_bp,   url_prefix='/contact')
    app.register_blueprint(admin_bp,     url_prefix='/admin')

    # ── Injecter 'now' dans tous les templates ────────────
    from datetime import datetime
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    return app