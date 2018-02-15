#! /usr/bin/env python3

from time import time
from time import sleep
from random import randint

import os  # environment vars



from urllib.request import urlopen

# https://docs.python.org/2/library/sched.html
#### SH = sched.scheduler(time, sleep)

PORT_NUMBER = int(os.getenv('HB_PORT', 8888))
HOST_NAME = os.getenv('HB_HOST', '127.0.0.1')
HB_SERVER_URL = os.getenv('HB_URL', "http://" + HOST_NAME + ":" + str(PORT_NUMBER))

# For the HB test client:
APP_ID = os.getenv('APP_ID', 'heartbeat')

# localhost:8888/hb_init?48&appid=test_client_python =>
#         /hb_init
#         [*] 
#         ['48', 'appid=test_client_python']
#         Accept-Encoding: identity
#         Host: localhost:8080
#         Connection: close
#         User-Agent: Python-urllib/2.7
#         
#         ID: Python-urllib/2.7@127.0.0.1

visits = {}

# overdue = 0 # Just for now... TODO: FIXME?: should be a part of visit data, right?!

def hb_read(msg):
    return str(urlopen(HB_SERVER_URL + msg).read().decode('UTF-8'))

def test_client():
    t = randint(2, 5)
    #    APP_ID =  # + str(randint(99999999, 9999999999)) # TODO: get unique ID from server?

    print("List HB apps: {}".format(hb_read("/list")))
    print("APP HB Status: {}".format(hb_read("/status")))

    tt = hb_read("/hb_init?" + str(t) + "&appid=" + APP_ID)
    print("Initial response: ", tt)

    overdue = 0

    i = 0
    #    for i in xrange(1, 25):
    #    while True:
    while tt != "dead":
        i = i + 1
        d = randint(0, int((int(t) * 5) / 4))

        try:
            if d > int(tt):
                print(d, " > ", tt, "?")
                overdue += 1
        except:
            pass

        print("heart-beat: ", i, "! Promise: ", t, ", Max: ", tt, ", Delay: ", d, " sec........ overdues?: ", overdue)
        sleep(d)

        # heartbeat: 
        t = randint(0, 5)

        #        print "List HB apps: " + urlopen(HB_SERVER_URL + "/list" ).read()
        #        print "APP HB Status: " + urlopen(HB_SERVER_URL + "/status" ).read()

        print("Ping: ", t)
        tt = hb_read("/hb_ping?" + str(t) + "&appid=" + APP_ID)
        print("Pong: ", tt)

    #        print "List HB apps: " + urlopen(HB_SERVER_URL + "/list" ).read()
    #        print "APP HB Status: " + urlopen(HB_SERVER_URL + "/status" ).read()

    print("Ups: we run out of time...")
    tt = hb_read("/hb_done?0" + "&appid=" + APP_ID)
    print("Goodbye message: ", tt)

    print("List HB apps: {}".format(hb_read("/list")))
    print("APP HB Status: {}".format(hb_read("/status")))

if __name__ == '__main__':
    test_client()
