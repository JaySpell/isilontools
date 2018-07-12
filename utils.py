import os
import json

def load_json(file_path):
    with open(file_path) as j:
        d = json.load(j)
        j.close()
        return d

def send_email(cost_dict):
    '''
    Will send an email to users specified in ADMINS
    with information for customer name, cost center &
    the support center rep who filled the request

    param: cost_dict({cfname: 'firstname', clname: 'lastname',
        cost_center: 'number', sc_rep: 'userid'})

    return: email send status
    '''
    from flask_mail import Message
    from app import mail
    from flask import render_template
    from external import config

    MAIL_SERVER = config.MAIL_SERVER
    MAIL_PORT = config.MAIL_PORT
    MAIL_USE_TLS = config.MAIL_USE_TLS
    MAIL_USE_SSL = config.MAIL_USE_SSL
    ADMINS = config.ADMINS

    msg = Message('Quota Space Addition', sender='QuotaMod@mhhs.org',
        recipients=ADMINS)

    msg.body = render_template('cost_center.txt',
            cust_lname=cost_dict['cust_lname'],
            cust_fname=cost_dict['cust_fname'],
            cost_cent=cost_dict['cost_cent'],
            space_add=cost_dict['space_add'],
            sc_account=cost_dict['sc_account'],
            work_order=cost_dict['work_order'],
            quota_before=cost_dict['quota_before'],
            quota_after=cost_dict['quota_after'],
            quota_path=cost_dict['quota_path']
        )
    msg.html = render_template('cost_center_email.html',
            cust_lname=cost_dict['cust_lname'],
            cust_fname=cost_dict['cust_fname'],
            cost_cent=cost_dict['cost_cent'],
            space_add=cost_dict['space_add'],
            sc_account=cost_dict['sc_account'],
            work_order=cost_dict['work_order'],
            quota_before=cost_dict['quota_before'],
            quota_after=cost_dict['quota_after'],
            quota_path=cost_dict['quota_path']
        )

    try:
        mail.send(msg)
        return "Email sent..."
    except:
        return "No email sent..."

def convert_to_bytes(my_int):
    new_num = my_int * 1024 * 1024 * 1024
    return new_num

def convert_to_GB(my_int):
    new_num = int((((my_int/1024)/1024)/1024))
    return new_num

def dict_to_tuple(a_list):
    new_list = []
    for a_dict in a_list:
        for key, value in a_dict.items():
            tuple_return = (value, key)
            new_list.append(tuple_return)
    return new_list
