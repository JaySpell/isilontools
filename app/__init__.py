from flask import Flask, g
from flask.ext.login import LoginManager
app = Flask(__name__)
app.config.from_object('config')
# from user import User


login_manager = LoginManager()
login_manager.login_view
login_manager.init_app(app)
login_manager.login_view = "login"

from app import views
