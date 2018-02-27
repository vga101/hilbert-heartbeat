#! /usr/bin/env python3

from __future__ import absolute_import, print_function, unicode_literals

import os

os.environ['APP_ID']='test_python'
#os.environ['HB_PORT']='8888'
os.environ['HB_HOST']='localhost'

import heartbeat

print(heartbeat.APP_ID)
print(heartbeat.HB_URL)

print(heartbeat.hb_init(500, "ups"))
print(heartbeat.hb_ping(1000, "ups"))
print(heartbeat.hb_done(2, "ups"))

