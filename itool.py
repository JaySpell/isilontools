from pprint import pprint
import urllib3
import secret
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

    def get_quota_summary(self):
        # Testing for API
        api_client = i_tools.ApiClient(self.configuration)
        api_instance = i_tools.QuotaApi(api_client)

        # Attempt connection
        try:
            api_response = api_instance.get_quota_quotas_summary()
            pprint(api_response)
        except ApiException as e:
            print("Exception when calling get_quota_summary -->:%s\n" % e)

    def get_quota_size(self, quota_id):
        """
        :param quota_id: Quota ID - to retrieve size
        :return: quota_info

        Function will take the current quota (current_quota) and add space
        - send to Isilon
        - return new quota (query_quota)
        """
        api_client = i_tools.ApiClientApi
        api_instance = i_tools.QuotaApi(api_client)


    def get_quota_size(self, quota_id):
        pass

    def find_quotas(self, search_string):
        '''
        Parse the quotas from the JSON files based on provided search string
        '''
        def get_all_quotas(dir_path, search_string):
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
        if plus_gb is not 100:
            add_space = 1073741824 * int(plus_gb)
        else:
            add_space = 107374182400
        quota = int(current_quota)
        h_limit = int(quota + add_space)
        a_limit = int((quota + add_space) * .95)

        api_client = i_tools.ApiClient(configuration)
        api_instance = i_tools.QuotaApi(api_client)

        q_quota = i_tools.QuotaQuota(
                thresholds={'advisory': a_limit, 'hard': h_limit}
            )
        try:
            api_instance.update_quota_quota(q_quota, quota_id)
        except ApiException as e:
            print("Exception when calling QuotaApi -> update_quota: %s\n" %e)
