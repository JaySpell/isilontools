from flask import Flask, g
from flask_login import LoginManager
from flask_mail import Mail
#from external import secret
from external import config

app = Flask(__name__)
app.config.from_object(config)
# from user import User

mail = Mail(app)

login_manager = LoginManager()
login_manager.login_view
login_manager.init_app(app)
login_manager.login_view = "login"

from app import views
