#! /usr/bin/env python3

import os  # os.getenv
import sys  # sys.exit

HB_SERVER_URL = os.getenv('HB_URL', "http://{}:{}".format(
                os.getenv('HB_HOST', '127.0.0.1'), int(os.getenv('HB_PORT', 8888))))

try:
    from urllib.request import urlopen
    S = urlopen(HB_SERVER_URL + "/status").read()
except:
    print("CRITICAL - cannot get heartbeat status from HB server!")
    sys.exit(2)

S = S.decode('utf-8')  # binary string on Python3!

if S.startswith("OK"):
    print(S)
    sys.exit(0)

if S.startswith("WARNING"):
    print(S)
    sys.exit(1)

if S.startswith("CRITICAL"):
    print(S)
    sys.exit(2)

# "UNKNOWN - ${msg}" => exit CODE: 3

print(S)
sys.exit(3)
