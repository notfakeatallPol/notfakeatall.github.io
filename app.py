import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create a base class for our SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with our base class
db = SQLAlchemy(model_class=Base)

# Create the Flask application
app = Flask(__name__)

# Configure the application
app.secret_key = os.environ.get("SESSION_SECRET", os.urandom(24).hex())
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///app.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configure maximum file upload size (16 MB)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["UPLOAD_FOLDER"] = "static/uploads"

# Initialize extensions
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

# Import models to ensure they're registered with SQLAlchemy
with app.app_context():
    import models  # noqa: F401
    from routes import register_routes
    from models import User, SystemConfig
    
    # Register all routes
    register_routes(app)
    
    # Create all tables
    db.create_all()
    
    # Check if system needs setup (no admin user exists)
    if User.query.filter_by(role="admin").first() is None:
        # Set setup mode
        app.config["SETUP_REQUIRED"] = True
    else:
        app.config["SETUP_REQUIRED"] = False

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))
