from flask import Flask
from flask_login import LoginManager
from flask_user import UserManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from config import config
from models import db, User, Role, Item

# Blueprints
from auth import auth as auth_blueprint
from api import api as api_blueprint
from main import main as main_blueprint

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)

    # Flask-User
    user_manager = UserManager(app, db, User)

    # Flask-Admin
    admin = Admin(app, name='Admin', template_mode='bootstrap3')
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Role, db.session))
    admin.add_view(ModelView(Item, db.session))

    # Register blueprints
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(api_blueprint, url_prefix='/api')
    app.register_blueprint(main_blueprint)

    return app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(ssl_context='adhoc')  # For HTTPS in dev