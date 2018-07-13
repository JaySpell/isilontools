#!/usr/bin/env python3
from external import secret
from itool import isitool

if __name__ == "__main__":
    itool = isitool()
    itool.get_all_quota()

    itool_p = isitool(**{'server': secret.get_phi_server()})
    itool_p.get_all_quota(**{'count': '100'})
