import ldap
from external import config

'''Get config'''
config = config.get_config()

'''Set the global variables'''
SERVER_LDAP = config['ldap_srv']
BASE_DN = config['base_dn']
AUTH_GROUP = config['ldap_grp']
UPN_SUFFIX = config['upn']

class ADAuth(object):

    def __init__(self, username, passwd, upn=UPN_SUFFIX):
        self.upn_id = username + upn
        self.password = passwd
        self.user = username

    def authenticate(self, server=SERVER_LDAP):
        conn = ldap.initialize('ldap://' + server)
        conn.protocol_version = 3
        conn.set_option(ldap.OPT_REFERRALS, 0)
        try:
            results = conn.simple_bind_s(self.upn_id, self.password)
        except ldap.INVALID_CREDENTIALS:
            error_return = "Username / Password incorrect..."
        except ldap.SERVER_DOWN:
            error_return = "Server unavailable..."
        except ldap.LDAPError as e:
            if type(e.message) == dict and e.message.has_key('desc'):
                return "Other LDAP error: " + e.message['desc']
            else:
                return "Other LDAP error: " + e

        return conn

    def check_group_for_account(self, basedn=BASE_DN,
                                auth_group=AUTH_GROUP):
        is_member = False

        try:
            conn = self.authenticate()
            s_user = "CN=" + self.upn_id.split('@')[0]

            results = conn.search_s(basedn,
                            ldap.SCOPE_SUBTREE,"(cn=%s)" % auth_group)

            for result in results[0][1]['member']:
                member_cn = result.decode("utf-8").split(',')[0]
                if member_cn.lower() == s_user.lower():
                    is_member = True
        except:
            pass

        return is_member
