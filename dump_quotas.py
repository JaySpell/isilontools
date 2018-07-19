#!/usr/bin/env python3
from external import config
from itool import isitool
config = config.get_config()

if __name__ == "__main__":
    itool = isitool()
    itool.get_all_quota()

    itool_p = isitool(**{'server': config['phi_server']})
    itool_p.get_all_quota(**{'count': '100'})
