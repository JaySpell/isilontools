import urllib2
import time
import json
import string
import secret
import pro_utils


class Tool(object):
    TEMPLATES = dict(PAPI_SESSION_AUTH='{{"username":"{user}", \
                                            "password":"{password}", \
                                            "services":["platform"]}}',
                     QUOTA_MODIFY='{{"thresholds":{{"advisory":{a_limit}, \
                                        "hard":{h_limit}}}}}')

    def __init__(self, server, **kwargs):
        self.name = self
        self.lastauthtimestamp = 0
        self.lastactiontimestamp = 0
        self.idletimeout = 0
        self.abstimeout = 0
        self.sessioncookie = ''
        self.mime_json = 'application/json'
        self.hdr_content_type = 'Content-Type'
        self.hdr_cookie = 'Cookie'
        self.idle_timeout_factor = 0.9
        self.timeout_factor = 0.75
        self.connection_state = False
        self.srv_url = server
        self.default_server = secret.get_server()
        self.default_user = secret.get_username()
        self.default_password = secret.get_password()
        self.json_path = secret.get_json_path()

    def islconnect(self, papi_user, papi_passwd, papi_cmd):
        if not active_connection():
            try:
                post_data = (
                    self.TEMPLATES['PAPI_SESSION_AUTH'].format(user=papi_user,
                                                               password=papi_passwd)
                )
                request = urllib2.Request(self.srv_url + papi_cmd, data=post_data)
                request.add_header(self.hdr_content_type, self.mime_json)
                response = urllib2.urlopen(request)

                # Pull out the absolute timeout and the inactivity timeout values
                json_resp = json.loads(response.read())

                # Setup all our timeout values:
                self.idletimeout = json_resp['timeout_inactive'] * self.idle_timeout_factor
                self.abstimeout = json_resp['timeout_absolute'] * self.timeout_factor
                self.lastauthtimestamp = time.time()
                self.lastactiontimestamp = time.time()

                # Get and save the session cookie
                self.cookie_crumbs = string.split(response.info()['set-cookie'], ';')
                self.sessioncookie = cookie_crumbs[0].strip()
                self.connection_state = True
            except urllib2.URLError as url_err:
                print("Exception trying to create session: %s" % url_err)
                print("===Code===\n%s" % url_err.code)
                print("===Headers===\n%s" % url_err.info())
                print("===Data===\n%s" % url_err.read())
                raise
        else:
            print("Using session cookie for authentication")

    def isilon_disconnect(self, papi_cmd):
        try:
            request = urllib2.Request(self.srv_url + papi_cmd('session',
                                                              'delete', options={'sessionid': self.sessioncookie}))
            request.add_header(self.hdr_content_type, self.mime_json)
            request.add_header(self.hdr_cookie, self.sessioncookie)
            request.get_method = lambda: 'DELETE'
            response = urllib2.urlopen(request)
            self.reset_auth_vals()
        except urllib2.URLError as url_err:
            print("Exception trying to delete session: %s" % url_err)
            print("===Code===\n%s" % url_err.code)
            print("===Headers===\n%s" % url_err.info())
            print("===Data===\n%s" % url_err.read())

    def active_connection():
        now = time.time()
        cond1 = now > (self.lastactiontimestamp + self.idletimeout)
        cond2 = now > (self.lastactiontimestamp + self.abstimeout)
        if (cond1 or cond2):
            self.connection_state = False
        else:
            self.connection_state = True
        return self.connection_state

    def reset_auth_vals():
        self.lastAuthTimestamp = 0
        self.lastActionTimestamp = 0
        self.idleTimeout = 0
        self.abstimeout = 0
        self.sessioncookie = ''


class QuotaTool(Tool):

    def __init__(self, server, **kwargs):
        self.rest_cmds = {
            'auth_cmd': '/session/1/session',
            'quota_query': '/platform/1/quota/quotas/',
            'quota_modify': '/platform/1/quota/quotaid',
            'quota_cmd': '/platform/1/quota/quotas'
        }
        super(QuotaTool, self).__init__(server)

    def get_quota_info(self, quota_id):
        if not self.active_connection():
            print("Please connect to Isilon using isilon_connect first..")
        else:
            try:
                request = urllib2.Request(svr_url + papi_cmd + quota_id)
                request.add_header(HDR_COOKIE, SessionCookie)
                response = urllib2.urlopen(request)
                self.reset_auth_vals()
                quota_info = pro_utils.get_quota_info(response)
                return quota_info

            except urllib2.URLError as url_err:
                print("Exception trying to delete session: %s" % url_err)
                print("===Code===\n%s" % url_err.code)
                print("===Headers===\n%s" % url_err.info())
                print("===Data===\n%s" % url_err.read())

    def get_quota_size(self, quota_id):
        '''
        Connects to Isilon via REST - quota info pulled from quota_id
        Response is run through a query by project tools to pull the
        threshold
        '''
        try:
            request = urllib2.Request(self.srv_url +
                self.rest_cmds['quota_query'] + quota_id)
            request.add_header(self.hdr_cookie, self.sessioncookie)
            response = urllib2.urlopen(request)
            self.reset_auth_vals()
            data = json.load(response)
            for quota in data['quotas']:
                threshold = quota['thresholds']['hard']
            current_thresh = int(threshold)

        except urllib2.URLError as url_err:
            print("Exception trying to delete session: %s" % url_err)
            print("===Code===\n%s" % url_err.code)
            print("===Headers===\n%s" % url_err.info())
            print("===Data===\n%s" % url_err.read())

    def isilon_find_quotas(self, search_string):
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

    def update_quota(self, quota_id, current_quota):
        """
        :param quota_id: Quota ID - to update
        :param current_quota: Size of current hard threshold
        :return: new_quota_info

        Function will take the current quota (current_quota) add 100GB
        - create URL
        - update quota
        - send to Isilon
        - return new quota (query_quota)
        """

        self.isilon_Connect()
        # Get the threshold data - my_int used so that input could be utilized in future
        my_int = 107374182400
        quota = int(current_quota)
        h_threshold = int(quota + my_int)
        a_threshold = int((quota + my_int) * .95)

        put_data = self.TEMPLATES['QUOTA_MODIFY'].format(a_limit=a_threshold,
            h_limit=h_threshold)
        try:
            request = urllib2.Request(self.srv_url +
                self.rest_cmds['quota_cmd'] + quota_id, data=put_data)
            request.add_header(self.hdr_content_type, self.mime_json)
            request.add_header(self.hdr_cookie, self.sessioncookie)
            request.get_method = lambda: 'PUT'
            response = urllib2.urlopen(request)
            self.reset_auth_vals()
        except urllib2.URLError as url_err:
            exception = ("Exception trying to update
                quota(update_quota_: % s" % url_err)
            exception=exception + ("===Code===\n%s" % url_err.code)
            print("===Headers===\n%s" % url_err.info())
            print("===Data===\n%s" % url_err.read())
