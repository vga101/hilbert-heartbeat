#! /usr/bin/env python3

from __future__ import absolute_import, print_function, unicode_literals

import signal
import sys
import os  # environment vars
import logging
from time import sleep, time
from random import randint

from urllib.request import urlopen
from urllib import request, parse

HB_URL = os.getenv('HB_URL', "http://{}:{}".format(
                os.getenv('HB_HOST', '127.0.0.1'), int(os.getenv('HB_PORT', 8888))))

# For the HB test client:
APP_ID = os.getenv('APP_ID', 'python_heartbeat_client_demo')

log = logging.getLogger(__name__)  #

__VERSION_ID = "$Id$"

#def main_exception_handler(type, value, tb):
#    import traceback
#    log.exception("Uncaught exception! Type: {0}, Value: {1}, TraceBack: {2}".format(type, value, traceback.format_tb(tb)))
#
#sys.excepthook = main_exception_handler # Install exception handler


def hb_http_get(msg, fallback=None):  # send a message via HTTP GET to HB Server specified by global HB_URL settiing
    try:
        with urlopen(HB_URL + msg) as f:
            return str(f.read().decode('UTF-8'))
    except BaseException as err:
        log.error("could not send [{}] to [{}]. Error: [{}]".format(msg, HB_URL, err))
        if fallback is None:
            raise err
        pass

    return str(fallback)


def hb_http_post(msg, data, fallback=None):  # send a message (incl. data) via HTTP POST to HB Server specified by global HB_URL settiing
    try:
        req = request.Request(HB_URL + msg, data=parse.urlencode(data).encode('utf-8'))  # Post Method is invoked if data != None
        with urlopen(req) as f:
            return str(f.read().decode('UTF-8'))
    except BaseException as err:
        log.error("could not send [{}] (with payload: [{}]) to [{}]. Error: [{}]".format(msg, data, HB_URL, err))
        if fallback is None:
            raise err
        pass

    return str(fallback)


def hb_ping(t, fallback=None):  # send HB_PING message to HB Server
    return hb_http_get("/hb_ping?{}&appid={}&cache_buster={}".format(t, APP_ID, time()), fallback)


def hb_done(t=0, fallback=None):  # send HB_DONE message to HB Server 
    return hb_http_post("/hb_done?{}&appid={}&cache_buster={}".format(t, APP_ID, time()), {'appid': APP_ID}, fallback)


def hb_init(t, fallback=None):  # send HB_INIT message to HB Server
    return hb_http_post("/hb_init?{}&appid={}&cache_buster={}".format(t, APP_ID, time()), {'appid': APP_ID}, fallback)


def hb_list(fallback=None):  # query the list of client IDs from HB Server
    return hb_http_get("/list?cache_buster={}".format(time()), fallback)


def hb_status(ID = None, fallback=None):  # query the status of a client host (or of specified application) from HB Server
    if ID is None:
        return hb_http_get("/status?cache_buster={}".format(time()), fallback)
    else:
        return hb_http_get("/status?0&appid={}&cache_buster={}".format(ID, time()), fallback)


def signal_handler(signal, frame):
    log.info('NOTE: You pressed Ctrl+C!')

    log.debug("List of all HB apps: {}".format(hb_list(fallback="SORRY: NO HB LIST RESPONSE")))
    log.debug("Statuses of all HB apps: {}".format(hb_status(fallback="SORRY: NO HB STATUS RESPONSE")))
    log.debug("Status of [{}]: {}".format(APP_ID, hb_status(APP_ID, fallback="SORRY: NO HB STATUS RESPONSE")))

    tt = hb_done(0, fallback="SORRY: NO HB DONE RESPONSE!")
    log.info("Goodbye message: [{}]".format(tt))

    log.debug("Final List of all HB apps: {}".format(hb_list(fallback="SORRY: NO HB LIST RESPONSE")))
    log.debug("Final Statuses of all HB apps: {}".format(hb_status(fallback="SORRY: NO HB STATUS RESPONSE")))
    log.debug("Final Status of [{}]: {}".format(APP_ID, hb_status(APP_ID, fallback="SORRY: NO HB STATUS RESPONSE")))

    sys.exit(0)



def test_client():
    _log = logging.getLogger()  # root logger!
    _log.setLevel(logging.DEBUG)
    logging.basicConfig(format='[%(asctime)s %(levelname)s] %(message)s', datefmt='%Y.%m.%d %I:%M:%S %p')
    # %(name)s            Name of the logger (logging channel)
    # %(levelno)s         Numeric logging level for the message (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    # %(levelname)s       Text logging level for the message ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
    # %(pathname)s        Full pathname of the source file where the logging call was issued (if available)
    # %(filename)s        Filename portion of pathname
    # %(module)s          Module (name portion of filename)
    # %(lineno)d          Source line number where the logging call was issued (if available)
    # %(funcName)s        Function name
    # %(created)f         Time when the LogRecord was created (time.time() return value)
    # %(asctime)s         Textual time when the LogRecord was created
    # %(msecs)d           Millisecond portion of the creation time
    # %(relativeCreated)d Time in milliseconds when the LogRecord was created,
    #                     relative to the time the logging module was loaded
    #                     (typically at application startup time)
    # %(thread)d          Thread ID (if available)
    # %(threadName)s      Thread name (if available)
    # %(process)d         Process ID (if available)
    # %(message)s         The result of record.getMessage(), computed just as the record is emitted

    signal.signal(signal.SIGINT, signal_handler)

    log.debug("List of all HB apps: {}".format(hb_list(fallback="SORRY: NO HB LIST RESPONSE")))
    log.debug("Statuses of all HB apps: {}".format(hb_status(fallback="SORRY: NO HB STATUS RESPONSE")))
    log.debug("Status of [{}]: {}".format(APP_ID, hb_status(APP_ID, fallback="SORRY: NO HB STATUS RESPONSE")))

    t = int(randint(100, 2000))
    tt = hb_init(t, fallback=t)
    log.info("Initial response: [{}]".format(tt))

    overdue = 0

    i = 0
    while True: # infinite look (until process termination)
        i = i + 1
        d = float(randint(0, int(t* 7.0)))

        try:
            if d > float(tt):
                log.debug("{} > {}!".format(d, tt))
                overdue += 1
        except:
            pass

        log.info("Heart-beat: {}! Promise: {}, Max: {}, Delay: {} sec... overdues so far: {}".format(i, t, tt, d, overdue))
        sleep(d/1000.0)

        # next heartbeat ping:
        t = int(randint(0, 3000))

        log.debug("Ping: [{}]".format(t))
        tt = hb_ping(t, fallback=t)
        log.debug("Pong: [{}]".format(tt))

    log.error("Ups: out of infinite loop: something went wrong?!")
    tt = hb_done(0, fallback="SORRY: NO HB DONE RESPONSE")
    log.info("Goodbye message: [{}]".format(tt))

    log.debug("Final List of all HB apps: {}".format(hb_list(fallback="SORRY: NO HB LIST RESPONSE")))
    log.debug("Final Statuses of all HB apps: {}".format(hb_status(fallback="SORRY: NO HB STATUS RESPONSE")))
    log.debug("Final Status of [{}]: {}".format(APP_ID, hb_status(APP_ID, fallback="SORRY: NO HB STATUS RESPONSE")))


if __name__ == '__main__':
    test_client()
