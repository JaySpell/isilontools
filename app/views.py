from .MyForm import MyForm, LoginForm
from app import app, login_manager
from flask import (render_template, flash, redirect,
    request, url_for, session, escape, g)
from flask.ext.login import (current_user, login_user,
    logout_user, login_required)
from isilon_tools import Isilon_Tools
from db import Quotas_DB, Users_DB
import pro_utils
from ad_auth import ADAuth
from user import User
import ldap

all_users = {}

@login_manager.user_loader
def load_user(username):
    '''
    Loads user from the currently authenticated AD user
    '''
    try:
        if username in all_users.keys():
            user = User(username)
            user.id = username
            return user
    except:
        return None

@app.route('/')
@app.route('/index')
def index():
    return render_template('test2.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if current_user.is_authenticated == True:
        error = 'Already logged in...'
        return redirect(url_for('quota'))

    myform = LoginForm()
    if myform.validate_on_submit():
        '''Get the username / password from form'''
        username = myform.username.data
        password = myform.password.data
        '''Attempt login using the ADAuth class'''
        auth = ADAuth(username, password)
        try:
            if auth.check_group_for_account() == True:
                all_users[username] = None
                user = User(unicode(auth.user))
                login_user(user)
                '''if not next_is_valid(next):
                    return flask.abort(400)'''
                return redirect(url_for('quota'))
        except:
            error = "Invalid credentials %s..." % user

    return render_template("login.html", form=myform, error=error)

@app.route('/quota', methods=['GET', 'POST'])
@login_required
def quota():
    myform = MyForm()
    if request.method == 'POST':
        name = request.form.get('name')
        session['search'] = name
        return redirect(url_for('quotas'))

    return render_template('form.html', title="Quota",
                                   form=myform)

@app.route('/quotas', methods=['GET', 'POST'])
@login_required
def quotas():
    '''
    This gets returned after a query is entered - it should do the following...
    - set the search_string from the session data
    - use the isilon_find_quotas to return a list of dictionaries with all quotas
    - IF there are quotas it should create a new form using the quotas_radio_return function
        -- new form will have a list of radio buttons (create
    :return:
    '''
    tool = Isilon_Tools()
    search_string = session['search']

    all_quotas = tool.isilon_find_quotas(search_string)
    if all_quotas == "NA":
        return render_template('quota_not_found.html')
    else:
        myform = quotas_radio_return(all_quotas)
        itemid = myform.itemid.data

    if myform.is_submitted():
        session['selected'] = myform.itemid.data
        return redirect(url_for('cost'))
    else:
        return render_template('test.html',form=myform, itemid=itemid)

@app.route('/quotas_return', methods=['GET', 'POST'])
def quotas_return():
    pass

@app.route('/cost', methods=['GET', 'POST'])
def cost():
    tool = Isilon_Tools()
    name = session['selected']
    myform = MyForm()

    if request.method == 'POST':
        '''Set variables from form data for the database'''
        cust_fname = myform.cust_fname.data
        cust_lname = myform.cust_lname.data
        cost_cent = myform.cost_center.data
        sc_account = current_user

        '''Add data to database'''
        quota_add = Quotas_DB.create(cust_fname=cust_fname,
            cust_lname=cust_lname, sc_account=sc_account, cost_cent=cost_cent)

        '''Set current quota == current_quota + 100GB'''
        current_thresh = tool.get_quota_size(name)
        tool.update_quota(name, current_thresh)
        new_thresh = tool.get_quota_size(name)
        new_thresh_GB = pro_utils.convert_to_GB(new_thresh)

        return render_template('finish.html', name=name, new_limit=new_thresh_GB)

    return render_template('cost.html', form=myform,
        btn_txt="Add Space", title="Enter Customer Name & Cost Center")

def quotas_radio_return(quotas):
    '''
    Creates a form - then adds the radio list
    - dict_to_tuple takes the list of dictionaries and returns a list of tuples
    - returns a form object
    :param quotas:
    :return:
    '''
    tuple_data = pro_utils.dict_to_tuple(quotas)

    form = MyForm()
    form.itemid.choices = tuple_data

    return form

@app.errorhandler(400)
def abort_page(e):
    return render_template('400.html', error=e), 400

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', error=e), 404
