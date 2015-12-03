from flask import Flask, g
from flask.ext.login import LoginManager
app = Flask(__name__)
app.config.from_object('config')
# from user import User


login_manager = LoginManager()
login_manager.login_view
login_manager.init_app(app)
login_manager.login_view = "login"
current_users = {}

from app import views
@login_manager.user_loader
def load_user(username):
    '''
    Loads user from the currently authenticated AD user
    '''
    try:
        if username in current_users.keys():
            user = User(username)
            return user
    except:
        return None
