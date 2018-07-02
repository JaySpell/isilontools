from pprint import pprint
import os
import urllib3
import secret
import utils
import isi_sdk_8_1_0 as i_tools
from isi_sdk_8_1_0.rest import ApiException

# Disable SSL warnings
urllib3.disable_warnings()

class isitool:

    def __init__(self, **kwargs):
        self.name = self
        self.default_server = secret.get_server()
        self.default_user = secret.get_username()
        self.default_password = secret.get_password()
        self.json_path = secret.get_json_path()

        # Connect Isilon
        self.configuration = i_tools.Configuration()
        self.configuration.username = self.default_user
        self.configuration.password = self.default_password
        self.configuration.verify_ssl = False
        self.configuration.host = self.default_server

    def get_quota_size(self, quota_id):
        """
        :param quota_id: Quota ID - to retrieve size
        :return: quota_info

        Function will get info on current quota
        - utilize get_quota_summary() to get info
        - return quota hard threshold size
        """

        quota_info = get_quota_summary(quota_id)
        r_data = quota_info.to_dict()

        return r_data['quotas'][0]['thresholds']['hard']

    def get_quota_summary(self, quota_id):
        """
        :param quota_id: Quota ID - to retrieve size
        :return: quota_info

        Function will get info on current quota
        - request from Isilon
        - return new quota (query_quota)
        """

        api_client = i_tools.ApiClient(self.configuration)
        api_instance = i_tools.QuotaApi(api_client)

        try:
            api_response = api_instance.get_quota_quota(quota_id)
        except ApiException as e:
            print("Exception when calling QuotaApi -> get_quota_size: %s\n" % e)

        return api_response

    def find_quotas(self, search_string):
        """
        :param search_string: str will be used in search

        Function will search all JSON files for quotas with search_string
        - Get list of all files in the specified directory
        - Search each one for the string
        - return quotas
        """

        def get_all_quotas(dir_path, search_string):
            allfiles = [f for f in os.listdir(dir_path) if os.isfile(join(dir_path, f))]
            none_found = "No match"
            all_quotas = []

            for file in allfiles:
                file_return = self._str_present_json(dir_path + file,
                                                    search_string)
                if file_return != "NA":
                    all_quotas.append(file_return)

            if len(all_quotas) = 0:
                all_quotas = "NA"

            return all_quotas

        quotas = get_all_quotas(self.json_path, search_string)

        return quotas


    def update_quota(self, quota_id, current_quota, plus_gb=100):
        """
        :param quota_id: Quota ID - to update
        :param current_quota: Size of current hard threshold
        :param plus_gb: default 100GB - can be overloaded for custom size
        :return: new_quota_info

        Function will take the current quota (current_quota) and add space
        - send to Isilon
        """
        # Determine size to add to quota
        if plus_gb != 100:
            add_space = 1073741824 * int(plus_gb)
        else:
            add_space = 107374182400

        quota = int(current_quota)
        h_limit = int(quota + add_space)
        a_limit = int((quota + add_space) * .95)

        # Add space using api calls
        api_client = i_tools.ApiClient(configuration)
        api_instance = i_tools.QuotaApi(api_client)
        q_quota = i_tools.QuotaQuota(
                thresholds={'advisory': a_limit, 'hard': h_limit}
            )

        try:
            api_instance.update_quota_quota(q_quota, quota_id)
        except ApiException as e:
            print("Exception when calling QuotaApi -> update_quota: %s\n" %e)


    def isilon_find_quotas(self, search_string):
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

                if len(return_quota.viewkeys()) = 0:
                    return_quota = "NA"

                return return_quota

        # Get all files in directory and put them in list
        allfiles = [f for f os.listdir(self.json_path) if os.isfile(
                        join(self.json_path, f))]

        all_quotas = []

        # Loop files use _str_present_json to find search str
        for file in allfiles:
            file_return = self._str_present_json(dir_path + file, search_string)
            if file_return != "NA":
                all_quotas.append(file_return)

        if len(all_quotas) = 0:
            all_quotas = "NA"

        return all_quotas
