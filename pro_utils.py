__author__ = 'kcup'
import os
from os import listdir
import json
from os.path import isfile, join
from pprint import pprint
from flask.ext.mail import Mail


'''
This will parse a directory of files that contain json files and return the one with
the matching string
'''
def find_file(dir_path, search_string):
    '''
    Open directory - search through all files for search_string - once found - return file
    :rtype : file
    :param dir_path:
    :param search_string:
    :return: file
    '''
    allfiles = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
    none_found = "No match"

    for file in allfiles:
        if find_data(search_string, dir_path + file):
            return file
        else:
            continue
    return none_found


def load_json(file_path):
    with open(file_path) as j:
        d = json.load(j)
        j.close()
        return d


'''
Load the json data - search for quota ID
'''
def find_data(search_string, file_to_open):
    all_data = load_json(file_to_open)
    for quota in all_data['quotas']:
        if search_string.lower() in quota['path'].lower():
            return True


def resume_str(filename):
    resume = "NA"
    if os.path.isfile(filename):
        all_data = load_json(filename)
        if all_data['resume'] == None:
            resume = "Done"
        else:
            resume = "?resume=" + all_data['resume']
        return resume
    else:
        return resume


def str_present_json(filename, search_string):
    '''
    Returns a dictionary with the path & quota ID if it is found...
    :param filename:
    :param search_string:
    :return:
    '''
    return_quota = {}

    if os.path.isfile(filename):
        all_data = load_json(filename)
        for quota in all_data['quotas']:
            if search_string.lower() in quota['path'].lower():
                return_quota = {quota['path']: quota['id']}

        if len(return_quota.viewkeys()) != 0:
            return return_quota
        else:
            return "NA"

def __threshold_json__(filename, search_string):
    return_threshold = None
    if os.path.isfile(filename):
        all_data = load_json(filename)
        for quota in all_data['quotas']:
            if search_string in quota['id']:
                return_threshold = quota['thresholds']['hard']
        if return_threshold != None:
            return return_threshold
        else:
            return "NA"

def get_threshold(dir_path, search_string):
    allfiles = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
    threshold = None

    for file in allfiles:
        threshold = __threshold_json__(dir_path + file, search_string)
        if threshold != "NA":
            break

    if threshold != None:
        return threshold
    else:
        return "NA"

def get_all_quotas(dir_path, search_string):
    '''
    Open directory - search through all files for search_string
    return list of dictionaries with path:quota_id
    :rtype : file
    :param dir_path:
    :param search_string:
    :return: file
    '''
    allfiles = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
    none_found = "No match"
    all_quotas = []

    for file in allfiles:
        file_return = str_present_json(dir_path + file, search_string)
        if file_return != "NA":
            all_quotas.append(file_return)

    if len(all_quotas) != 0:
        return all_quotas
    else:
        return "NA"

def get_all_quota_files(dir_path, search_string):
    '''
    Open directory - search through all files for search_string
    return list of filenames containing quotas...
    :rtype : file
    :param dir_path:
    :param search_string:
    :return: file
    '''
    allfiles = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
    none_found = "No match"
    all_files = []

    for file in allfiles:
        file_return = str_present_json(dir_path + file, search_string)
        if file_return != "NA":
            all_files.append(file)

    if len(all_files) != 0:
        return all_quotas
    else:
        return "NA"


# Load the json data - search for specific string ID
def find_quota(user_name, filename):
    allfiles = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
    quota_threshold = []

    all_data = load_json(filename)
    for quota in all_data['quotas']:
        if user_name.lower() in quota['path'].lower():
            quota_id = quota['id']
            # pprint(quota['id'])
            # pprint(quota['path'])
    return quota_id

def get_quota_info(filename, search_string):
    '''
    Returns a dictionary with the threshold information....
    :param filename:
    :param search_string:
    :return: threshold for quota
    '''
    return_quota = {}

    if os.path.isfile(filename):
        all_data = load_json(filename)
        for quota in all_data['quotas']:
            if search_string.lower() in quota['path'].lower():
                return_quota = {quota['path']: quota['id']}

        if len(return_quota.viewkeys()) != 0:
            return return_quota
        else:
            return "NA"


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

def get_new_threshold(response):
    data = json.load(response)
    for quota in data['quotas']:
        threshold = quota['thresholds']['hard']
    return int(threshold)

def send_the_email():
    pass
