from pprint import pprint
import os
import json
import urllib3
from external import config
#import sys
#sys.path.append('/home/jspell/Documents/dev/quotamod/isilontools/external')
#import config
import utils
import isi_sdk_8_1_0 as i_tools
from isi_sdk_8_1_0.rest import ApiException

# Disable SSL warnings
urllib3.disable_warnings()

class isitool:

    def __init__(self, **kwargs):
        self.name = self
        self.config = config.get_config()
        self.default_server = kwargs.get('server', self.config['isl_server'])
        self.default_user = self.config['isl_user']
        self.default_password = self.config['isl_pass']
        self.json_path = self.config['pro_dir'] +\
                         self.config['config_dir'] +\
                         self.config['quota_dir']

        # Connect Isilon
        self.configuration = i_tools.Configuration()
        self.configuration.username = str(self.default_user)
        self.configuration.password = str(self.default_password)
        self.configuration.verify_ssl = False
        self.configuration.host = self.default_server

    def get_quota_size(self, quota_id):
        '''
        :param quota_id: Quota ID - to retrieve size
        :return: quota_info

        Function will get info on current quota
        - utilize get_quota_summary() to get info
        - return quota hard threshold size
        '''

        quota_info = self.get_quota_summary(quota_id)
        r_data = quota_info.to_dict()

        return r_data['quotas'][0]['thresholds']['hard']

    def get_quota_summary(self, quota_id):
        '''
        Get a quota summary from Isilon through REST call

        :param quota_id: Quota ID - to retrieve size
        :return: quota_info

        Function will get info on current quota
        - request from Isilon
        - return new quota (query_quota)
        '''

        api_client = i_tools.ApiClient(self.configuration)
        api_instance = i_tools.QuotaApi(api_client)

        try:
            api_response = api_instance.get_quota_quota(quota_id)
        except ApiException as e:
            print("Exception when calling QuotaApi -> get_quota_size: %s\n" % e)

        return api_response

    def update_quota(self, quota_id, current_quota, plus_gb=50):
        """
        :param quota_id: Quota ID - to update
        :param current_quota: Size of current hard threshold
        :param plus_gb: default 50GB - can be overloaded for custom size
        :return: new_quota_info

        Function will take the current quota (current_quota) and add space
        - send to Isilon
        """

        '''Determine size to add to quota'''
        if plus_gb >= 50:
            add_space = 1073741824 * int(plus_gb)
        else:
            add_space = int(53687091200)

        quota = int(current_quota)
        h_limit = int(quota + add_space)
        a_limit = int((quota + add_space) * .95)

        '''Add space using api calls'''
        api_client = i_tools.ApiClient(self.configuration)
        api_instance = i_tools.QuotaApi(api_client)
        q_quota = i_tools.QuotaQuota(
                thresholds={'advisory': a_limit, 'hard': h_limit}
            )

        try:
            api_instance.update_quota_quota(q_quota, quota_id)
        except ApiException as e:
            print("Exception when calling QuotaApi -> update_quota: %s\n" %e)

    def find_quotas(self, search_string):
        '''
        Open directory - search through all files for search_string
        return list of dictionaries with path:quota_id
        :rtype : file
        :param dir_path:
        :param search_string:
        :return: file
        '''
        def _str_present_json(filename, search_string):
            '''
            Returns a dictionary with the path & quota ID if it is found...
            :param filename:
            :param search_string:
            :return:
            '''
            return_quota = {}

            if os.path.isfile(filename):
                all_data = utils.load_json(filename)
                for quota in all_data['quotas']:
                    if search_string.lower() in quota['path'].lower():
                        return_quota = {quota['path']: quota['id']}

                if len(return_quota.keys()) == 0:
                    return_quota = "NA"

                return return_quota

        # Get all files in directory and put them in list
        allfiles = [f for f in os.listdir(self.json_path) if os.path.isfile(
                    os.path.join(self.json_path, f))]

        all_quotas = []

        # Loop files use _str_present_json to find search str
        for file in allfiles:
            file_return = _str_present_json(self.json_path + file, search_string)
            if file_return != "NA":
                all_quotas.append(file_return)

        if len(all_quotas) == 0:
            all_quotas = "NA"

        return all_quotas

    def get_quota_info(self, quota_id):
        '''
        Get the quota based on the quota_id passed
        :param quota_id: Quota ID - to update
        :return: quota_info
        '''
        api_client = i_tools.ApiClient(self.configuration)
        api_instance = i_tools.QuotaApi(api_client)

        try:
            api_response = api_instance.get_quota_quota(quota_id)
        except ApiException as e:
            print("Exception when calling QuotaApi --> get_quota_info: %s\n" %e)

        quota_info = api_response.to_dict()

        return quota_info

    def get_all_quota(self, **kwargs):
        '''
        Function loops through the query and dumps all
        quotas to a series of files
        - opens new file for each query
        - save out the file
         Query should run till output of resume == None
         :return:
        '''
        count = kwargs.get('count', 1)
        name_prefix = kwargs.get('filename', 'json_out')
        limit = kwargs.get('limit', 1000)

        api_client = i_tools.ApiClient(self.configuration)
        api_instance = i_tools.QuotaApi(api_client)

        '''Dump the output of the query to a file'''
        def dump_to_file(api_response, count):
            filename = self.json_path + name_prefix + str(count)
            data = api_response.to_dict()
            with open(filename, 'w') as outfile:
                outfile.truncate()
                json.dump(data, outfile)


        '''Get first set of quotas'''
        api_response = api_instance.list_quota_quotas(limit=limit)
        dump_to_file(api_response, count)

        '''Loop until there are no quota'''
        while api_response.to_dict()['resume'] is not None:
            api_response = api_instance.list_quota_quotas(
                    resume=api_response.resume.encode("utf-8"))
            dump_to_file(api_response, count)
            print(api_response.resume)
            count += 1
