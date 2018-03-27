#! /usr/bin/env python3

from __future__ import absolute_import, print_function, unicode_literals

import os  # os.getenv
import sys  # sys.exit
from urllib.request import urlopen
from time import sleep, time

HB_SERVER_URL = os.getenv('HB_URL', "http://{}:{}".format(
                os.getenv('HB_HOST', '127.0.0.1'), int(os.getenv('HB_PORT', 8888))))

APP_ID = os.getenv('APP_ID', None)

def hb_http_get(msg, fallback=None):  # send a message via HTTP GET to HB Server specified by global HB_URL settiing
    try:
        with urlopen(HB_SERVER_URL + msg) as f:
            return str(f.read().decode('UTF-8')) # binary string on Python3!
    except BaseException as err:
#        log.error("could not send [{}] to [{}]. Error: [{}]".format(msg, HB_URL, err))
        if fallback is None:
            raise err
        pass

    return str(fallback)

def hb_status(ID = None, fallback=None):  # query the status of a client host (or of specified application) from HB Server
    if ID is None:
        return hb_http_get("/status?cache_buster={}".format(time()), fallback)
    else:
        return hb_http_get("/status?0&appid={}&cache_buster={}".format(ID, time()), fallback)

try:
    S = hb_status(APP_ID)  # if APP_ID is given - check that individual app, otherwise: host status is queried
except:
    print("CRITICAL - cannot get heartbeat status from HB server!")
    sys.exit(2)


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
