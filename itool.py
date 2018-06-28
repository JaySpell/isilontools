import urllib3
import secret
import isi_sdk_8_1_0 as i_tools
from i_tools.rest import ApiException

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
        self.api_client = i_tools.ApiClient(self.configuration)
        self.protocols_api = i_tools.ProtocolsApi(self.api_client)
