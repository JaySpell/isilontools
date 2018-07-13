from .MyForm import MyForm, LoginForm, QuotaForm, RadioForm
from app import app, login_manager
from flask import (render_template, flash, redirect,
                   request, url_for, session, escape, g)
from flask_login import (current_user, login_user,
                             logout_user, login_required)
from itool import isitool
from db import Quota_Update, A_User
import utils
from ad_auth import ADAuth
from user import User
import ldap
import urllib3

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
    return redirect(url_for('login'))


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
                user = User(str(auth.user))
                login_user(user)
                return redirect(url_for('quota'))
            else:
                raise ValueError('not member of AD group ')
        except ValueError as e:
            error = str(e) + (" invalid credentials %s..." % username)

    return render_template("login.html", form=myform, error=error)


@app.route('/quota', methods=['GET', 'POST'])
@login_required
def quota():
    myform = QuotaForm()
    if myform.validate_on_submit():
        name = request.form.get('name')
        session['search'] = name
        return redirect(url_for('quotas'))
    return render_template('quota.html', title="Quota",
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
    tool = isitool()
    search_string = session['search']

    all_quotas = tool.find_quotas(search_string)
    if all_quotas == "NA":
        return render_template('quota_not_found.html')
    else:
        myform = quotas_radio_return(all_quotas)
        itemid = myform.itemid.data

    if myform.is_submitted():
        session['selected'] = myform.itemid.data

        '''Grab the path and set it in session for passing on'''
        for quota in all_quotas:
            for path, id in quota.items():
                if id == myform.itemid.data:
                    session['select-path'] = path
        return redirect(url_for('cost'))
    else:
        return render_template('quotas.html', form=myform, itemid=itemid)


@app.route('/cost', methods=['GET', 'POST'])
@login_required
def cost():
    name = session['selected']
    path = session['select-path']

    '''Checks whether P drive or not'''
    if 'phi_access' in path.lower():
        from external import secret
        overload_server = {'server': secret.get_phi_server()}
        tool = isitool(**overload_server)
    else:
        tool = isitool()

    myform = MyForm()
    myform.name = name[1]

    if myform.validate_on_submit():
        '''Set variables from form data for the database'''
        cust_fname = myform.cust_fname.data
        cust_lname = myform.cust_lname.data
        cost_cent = myform.cost_center.data
        space_add = myform.space_add.data
        work_order = myform.work_order.data
        sc_account = current_user

        try:
            '''Get quota info'''
            quota_info = tool.get_quota_info(name)

            '''Set current quota == current_quota + 100GB'''
            current_thresh = int(quota_info['quotas'][0]['thresholds']['hard'])
            if space_add is not None:
                if space_add < 100:
                    space_add = 100
                tool.update_quota(name, current_thresh, plus_gb=int(space_add))
            else:
                tool.update_quota(name, current_thresh)
                space_add = 100

            '''Query for new quota size / convert to GB'''
            new_quota_info = tool.get_quota_info(name)
            new_quota_thresh = int(new_quota_info['quotas'][0]['thresholds']['hard'])
            new_thresh_GB = utils.convert_to_GB(new_quota_thresh)

        except:
            return render_template('404.html', error="Could not add space to quota....")

        '''Add data to database'''
        quota_add = Quota_Update.create(
            cust_fname=cust_fname,
            cust_lname=cust_lname,
            sc_account=sc_account,
            cost_cent=cost_cent,
            space_add=space_add,
            work_order=work_order,
            quota_path=quota_info['quotas'][0]['path'],
            quota_id=name,
            quota_before=current_thresh,
            quota_after=new_quota_thresh
        )

        '''Send email'''
        cost_dict = {
            'cust_fname': cust_fname,
            'cust_lname': cust_lname,
            'cost_cent': cost_cent,
            'quota_id': name,
            'space_add': space_add,
            'work_order': work_order,
            'sc_account': sc_account,
            'quota_before': current_thresh,
            'quota_after': new_quota_thresh,
            'quota_path': quota_info['quotas'][0]['path']
        }

        email_status = utils.send_email(cost_dict)

        return render_template('finish.html', name=name,
                               new_limit=new_thresh_GB, email_status=email_status)

    print(myform.errors)
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
    tuple_data = utils.dict_to_tuple(quotas)

    form = RadioForm()
    form.itemid.choices = tuple_data

    return form


@app.errorhandler(400)
def abort_page(e):
    return render_template('400.html', error=e), 400


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', error=e), 404
