__author__ = 'kcup'
'''
Class used to connect to Isilon and query from it

AVAILABLE FUNCTIONS

#Following require quotas have been dumped to txt file for speed purposes
quota_query(quota_id) -- requires quota id
quota_id_query(user/group) -- finds quota based on string -- requires name of user or group to modify quota for

#Following require connection to isilon
isilon_connect
modify_quota(quota_id)
'''

import urllib2
import time
import json
import string
import secret

import pro_utils

LastAuthTimestamp = 0
LastActionTimestamp = 0
IdleTimeout = 0
ABSTimeout = 0
SessionCookie = ''
AppDirectory = secret.get_app_dir()
TEMPLATES = dict(PAPI_SESSION_AUTH='{{"username":"{user}","password":"{password}","services":["platform"]}}',
                 QUOTA_MODIFY='{{"thresholds":{{"advisory":{a_limit},"hard":{h_limit}}}}}')
DEFAULT_SERVER = secret.get_server()
DEFAULT_USER = secret.get_username()
DEFAULT_PASSWORD = secret.get_password()
MIME_JSON = "application/json"
HDR_CONTENT_TYPE = "Content-Type"
HDR_COOKIE = "Cookie"
IDLE_TIMEOUT_FACTOR = 0.9
TIMEOUT_FACTOR = 0.75
APP_PATH = secret.get_json_path()

# REST QUERY STRINGS
AUTH_CMD = "/session/1/session"
QUOTA_QUERY = "/platform/1/quota/quotas/"
QUOTA_MODIFY = "/platform/1/quota/quotaid"
QUOTA_CMD = "/platform/1/quota/quotas/"


class Isilon_Tools(object):
    def __init__(self):
        self.name = self

    def PAPI_TSUpdate(self):
        global LastActionTimestamp
        LastActionTimestamp = time.time()

    def isilon_Connect(self, svr_url=DEFAULT_SERVER,
                       papi_user=DEFAULT_USER,
                       papi_user_password=DEFAULT_PASSWORD, papi_cmd=AUTH_CMD):
        global LastAuthTimestamp
        global LastActionTimestamp
        global IdleTimeout
        global ABSTimeout
        global SessionCookie

        now = time.time()
        if (now > (LastActionTimestamp + IdleTimeout) or now > (LastActionTimestamp + ABSTimeout)):
            try:
                post_data = TEMPLATES['PAPI_SESSION_AUTH'].format(user=papi_user, password=papi_user_password)
                request = urllib2.Request(svr_url + papi_cmd, data=post_data)
                request.add_header(HDR_CONTENT_TYPE, MIME_JSON)
                response = urllib2.urlopen(request)

                # Save authentication values

                # Pull out the absolute timeout and the inactivity timeout values
                json_resp = json.loads(response.read())

                # Setup all our timeout values:
                IdleTimeout = json_resp['timeout_inactive'] * IDLE_TIMEOUT_FACTOR
                ABSTimeout = json_resp['timeout_absolute'] * TIMEOUT_FACTOR
                LastAuthTimestamp = time.time()
                self.PAPI_TSUpdate()

                # Get and save the session cookie
                cookie_crumbs = string.split(response.info()['set-cookie'], ';')
                SessionCookie = cookie_crumbs[0].strip()
            except urllib2.URLError as url_err:
                print("Exception trying to create session: %s" % url_err)
                print("===Code===\n%s" % url_err.code)
                print("===Headers===\n%s" % url_err.info())
                print("===Data===\n%s" % url_err.read())
                raise
        else:
            print("Using session cookie for authentication")

    def isilon_disconnect(self, svr_url=DEFAULT_SERVER, papi_cmd=AUTH_CMD):
        global SessionCookie
        try:
            request = urllib2.Request(svr_url + papi_cmd('session', 'delete', options={'sessionid': SessionCookie}))
            request.add_header(HDR_CONTENT_TYPE, MIME_JSON)
            request.add_header(HDR_COOKIE, SessionCookie)
            request.get_method = lambda: 'DELETE'
            response = urllib2.urlopen(request)

            # Reset authentication values
            LastAuthTimestamp = 0
            LastActionTimestamp = 0
            IdleTimeout = 0
            ABSTimeout = 0
            SessionCookie = ''
        except urllib2.URLError as url_err:
            print("Exception trying to delete session: %s" % url_err)
            print("===Code===\n%s" % url_err.code)
            print("===Headers===\n%s" % url_err.info())
            print("===Data===\n%s" % url_err.read())

    def isilon_Query_Quota(self):
        '''
          Function loops through the query
          - opens new file for each query
          - save out the file
          Query should run till output of resume == None
          :return:
        '''
        # Set variables - including globals
        global AppDirectory
        count = 1
        incomplete = True

        # Connect to Isilon
        self.isilon_Connect()

        # Query Isilon for quota data until resume == None
        # dump data to multiple files - beginning with 1
        while incomplete:
            filename = AppDirectory + "json_out" + str(count)

            # If this is the first run there will not be a file to query - in this case
            # continue with the filename 1 - else grab previous run file
            if count > 1:
                resume_file_name = AppDirectory + "json_out" + str(count - 1)
                resume = pro_utils.resume_str(resume_file_name)
            else:
                resume = "NA"

            if resume != "Done":
                response = self.isilon_Run_Query(resume)
                data = json.load(response)
                with open(filename, 'w') as outfile:
                    outfile.truncate()
                    json.dump(data, outfile)
                count += 1
            else:
                incomplete = False

    def isilon_Run_Query(self, resume, svr_url=DEFAULT_SERVER, PAPI_Content_Cmd=QUOTA_CMD):
        global SessionCookie
        global AppDirectory

        if resume == "NA":
            resume_param = ""
        else:
            resume_param = resume

        try:
            request = urllib2.Request(svr_url + PAPI_Content_Cmd + resume_param)
            request.add_header(HDR_COOKIE, SessionCookie)
            response = urllib2.urlopen(request)
            return response

        except urllib2.URLError as url_err:
            print("Exception trying to delete session: %s" % url_err)
            print("===Code===\n%s" % url_err.code)
            print("===Headers===\n%s" % url_err.info())
            print("===Data===\n%s" % url_err.read())

    def isilon_find_quotas(self, search_string):
        '''

        :param search_string:
        :return:
        '''

        #Set variables - including globals
        global AppDirectory

        quotas = pro_utils.get_all_quotas(AppDirectory, search_string)
        return quotas
        '''
        for quota in quotas:
            for path, id in quota.iteritems():
                print(path, id)
        '''

    def isilon_quota_modify(self, search_string, new_size, svr_url=DEFAULT_SERVER,
                            papi_cmd=QUOTA_CMD, my_template=TEMPLATES):
        '''
        Utilize pro_utils to find the file containing user then use to find the quota id
        :param svr_url:
        :param papi_thres:
        :param papi_cmd:
        :param search_string
        :return:
        '''
        global AppDirectory
        global SessionCookie
        global LastAuthTimestamp
        global LastActionTimestamp
        global IdleTimeout
        global ABSTimeout
        global TEMPLATES

        self.isilon_Connect()

        filename = pro_utils.find_file(AppDirectory, search_string)

        if filename != "No match":
            quota_id = pro_utils.find_quota(search_string, AppDirectory + filename)

            # Get the threshold data
            my_int = new_size
            h_threshold = int(pro_utils.convert_to_bytes(my_int))
            a_threshold = int(pro_utils.convert_to_bytes(int(my_int * .95)))

            put_data = my_template['QUOTA_MODIFY'].format(a_limit=a_threshold, h_limit=h_threshold)
            print(put_data)

            try:
                request = urllib2.Request(svr_url + papi_cmd + quota_id, data=put_data)
                request.add_header(HDR_CONTENT_TYPE, MIME_JSON)
                request.add_header(HDR_COOKIE, SessionCookie)
                request.get_method = lambda: 'PUT'
                response = urllib2.urlopen(request)

                # Reset authentication values
                LastAuthTimestamp = 0
                LastActionTimestamp = 0
                IdleTimeout = 0
                ABSTimeout = 0
                SessionCookie = ''
            except urllib2.URLError as url_err:
                print("Exception trying to update quota session: %s" % url_err)
                print("===Code===\n%s" % url_err.code)
                print("===Headers===\n%s" % url_err.info())
                print("===Data===\n%s" % url_err.read())

        else:
            print("Quota not found!!!")

    def update_quota(self, quota_id, current_quota, svr_url=DEFAULT_SERVER, papi_cmd=QUOTA_CMD, my_template=TEMPLATES):
        """
        :param quota_id: Quota ID - to update
        :param current_quota: Size of current hard threshold
        :param svr_url:
        :param papi_cmd:
        :param my_template:
        :return: new_quota_info

        Function will take the current quota (current_quota) add 100GB to it - create URL string
        to update the quota and send it to Isilon - it will then return the new quota info using the query_quota..
        """

        global AppDirectory
        global SessionCookie
        global LastAuthTimestamp
        global LastActionTimestamp
        global IdleTimeout
        global ABSTimeout
        global TEMPLATES

        self.isilon_Connect()

        # Get the threshold data - my_int used so that input could be utilized in future
        my_int = 107374182400
        quota = int(current_quota)
        h_threshold = int(quota + my_int)
        a_threshold = int((quota + my_int) * .95)

        put_data = my_template['QUOTA_MODIFY'].format(a_limit=a_threshold, h_limit=h_threshold)

        try:
            request = urllib2.Request(svr_url + papi_cmd + quota_id, data=put_data)
            request.add_header(HDR_CONTENT_TYPE, MIME_JSON)
            request.add_header(HDR_COOKIE, SessionCookie)
            request.get_method = lambda: 'PUT'
            response = urllib2.urlopen(request)

            # Reset authentication values
            LastAuthTimestamp = 0
            LastActionTimestamp = 0
            IdleTimeout = 0
            ABSTimeout = 0
            SessionCookie = ''
        except urllib2.URLError as url_err:
            exception = ("Exception trying to update quota (update_quota_: %s" % url_err)
            exception = exception + ("===Code===\n%s" % url_err.code)
            print("===Headers===\n%s" % url_err.info())
            print("===Data===\n%s" % url_err.read())

    def get_quota_size(self, quota_id, svr_url=DEFAULT_SERVER, papi_cmd=QUOTA_QUERY, my_template=TEMPLATES):
        global AppDirectory
        global SessionCookie
        global LastAuthTimestamp
        global LastActionTimestamp
        global IdleTimeout
        global ABSTimeout
        global TEMPLATES

        self.isilon_Connect()

        try:
            request = urllib2.Request(svr_url + papi_cmd + quota_id)
            request.add_header(HDR_COOKIE, SessionCookie)
            response = urllib2.urlopen(request)

            # Reset authentication values
            LastAuthTimestamp = 0
            LastActionTimestamp = 0
            IdleTimeout = 0
            ABSTimeout = 0
            SessionCookie = ''

            current_thresh = pro_utils.get_new_threshold(response)
            return current_thresh

        except urllib2.URLError as url_err:
            print("Exception trying to delete session: %s" % url_err)
            print("===Code===\n%s" % url_err.code)
            print("===Headers===\n%s" % url_err.info())
            print("===Data===\n%s" % url_err.read())
