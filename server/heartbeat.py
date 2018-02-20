#! /usr/bin/env python3

# import sched, time
from time import time
from time import sleep
from random import randint
from threading import Timer

import os  # environment vars

# import urllib.request, urllib.parse, urllib.error  # what? why?
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote

# https://docs.python.org/2/library/sched.html
#### SH = sched.scheduler(time, sleep)

PORT_NUMBER = int(os.getenv('HB_PORT', 8888))
HOST_NAME = os.getenv('HB_HOST', '127.0.0.1')
HB_SERVER_URL = os.getenv('HB_URL', "http://" + HOST_NAME + ":" + str(PORT_NUMBER))


visits = {}

# overdue = 0 # Just for now... TODO: FIXME?: should be a part of visit data, right?!

# TODO: add logging, fix for Python2 and Python3? Better Timer handling!

def toolate(ID):
    ts = time()
    print("[", ts, "] [", ID, "]: ", visits[ID])

    d = visits[ID]
    # Collect statistics about ID    

    if d[3] > 6:
        print("TOO overdue - dropping!!!")  # TODO: early detection of overdue clients!!???
        del visits[ID]
    else:
        visits[ID] = (d[0], d[1], Timer(d[1], toolate, [ID]), d[3] + 1)
        visits[ID][2].start()  # Another Chance???


class MyHandler(BaseHTTPRequestHandler):
    def status(s, ID):
        """
        s: .headers, .client_address, .command, .path, .request_version, .raw_requestline
        """
        d = visits[ID]

        t = d[0]
        dd = d[1]
        od = d[3]

        app = "application [" + str(ID) + "]| od=" + str(od) + ";1;3;0;10 delay=" + str(dd) + ";;; "

        ## STATUS CODE???
        if od <=2:
            s.wfile.write(bytes("OK - fine " + app, 'UTF-8'))
        elif od > 2:
            s.wfile.write(bytes("WARNING - somewhat late " + app, 'UTF-8'))
        elif od > 4:
            s.wfile.write(bytes("CRITICAL - quite late " + app, 'UTF-8'))

    def do_GET(s):
        global visits
        #        global overdue

        s.send_response(200)
        s.send_header('Content-type', 'text/html')
        s.send_header('Access-Control-Allow-Origin', '*')
        s.end_headers()

        # NOTE: URL "localhost:8888/hb_init?48&appid=test_client_python" should be parsed as follows:
        #         '/hb_init', '48', 'appid=test_client_python']
        ### TODO: FIXME: the following url parsing is neither failsafe nor secure! :-(
        path, _, tail = s.path.partition('?')
        path = unquote(path)

        if path == "/list":
            # NOTE: list currently tracked visits
            for k, v in visits.items():
                s.wfile.write(bytes(str(k) + "\n", 'UTF-8'))
            return

        query = tail.split('&')

        if path == "/status":
            # NOTE: query the status of currently tracked visits (compatible with )
            if tail != "":
                ID = query[0].split('=')[1]  # + " @ " + s.client_address[0] # " || " + s.headers['User-Agent']
                if ID in visits:
                    s.status(ID)
                else:
                    s.wfile.write(bytes("CRITICAL - no application record for " + str(ID), 'UTF-8'))
            else:
                if len(visits) == 1:
                    ID = next(iter(visits.keys()))
                    s.status(ID)
                elif len(visits) > 1:
                    s.wfile.write(bytes("WARNING - multiple (" + str(len(visits)) + ") applications", 'UTF-8'))
                else:
                    s.wfile.write(bytes("UNKNOWN - no heartbeat clients at the moment...", 'UTF-8'))

            return

        # PARSING: s.path -->>> path ? T & appid = ID        
        T = int(query[0])
        ID = query[1].split('=')[1] + " @ " + s.client_address[0]  # " || " + s.headers['User-Agent']

        if ID in visits:
            print("PREVIOUS STATE", visits[ID])
            visits[ID][2].cancel()  # !

        ts = time()

        if (((path == "/hb_init") or (path == "/hb_ping")) and (ID not in visits)):
            # Hello little brother! Big Brother is watching you!
            print("Creation from scratch : ", ID, " at ", ts)
            T = T + 1  # max(10, (T*17)/16)
            visits[ID] = (ts, T, Timer(T, toolate, [ID]), 0)
            s.wfile.write(bytes(str(T), 'UTF-8'))  # ?
            visits[ID][2].start()

        elif ((path == "/hb_done") and (ID in visits)):
            print("Destruction: ", ID, " at ", ts)
            del visits[ID]
            s.wfile.write(bytes("So Long, and Thanks for All the Fish!", 'UTF-8'))

        elif (((path == "/hb_ping") or (path == "/hb_init")) and (ID in visits)):  #
            # TODO: make sure visits[ID] exists!
            print("HEART-BEAT for: ", ID, " at ", ts)  # Here i come again... 
            lastts = visits[ID][0]
            lastt = visits[ID][1]
            overdue = visits[ID][3]
            #            if (ts - lastts) > lastt: # Sorry Sir, but you are too late :-(
            #                overdue += 1

            if overdue > 3:
                print("Overdue counter: ", overdue)  # TODO: early detection of overdue clients!!???
                # s.wfile.write("dead")  # ?
            #                del visits[ID] #??
            T = T + 1  # max(3, (T*11)/8)
            visits[ID] = (ts, T, Timer(T, toolate, [ID]), 0)
            s.wfile.write(bytes(str(T), 'UTF-8'))
            visits[ID][2].start()
            # WHAT ELSE????
        return

    def do_POST(s):
        MyHandler.do_GET(s)

def test_server(HandlerClass=MyHandler, ServerClass=HTTPServer, protocol="HTTP/1.0"):
    """Test the HTTP request handler class.
    """

    server_address = (HOST_NAME, PORT_NUMBER)

    HandlerClass.protocol_version = protocol
    httpd = ServerClass(server_address, HandlerClass)

    sa = httpd.socket.getsockname()
    print("Serving HTTP on", sa[0], "port", sa[1], "...")
    httpd.serve_forever()

if __name__ == '__main__':
    test_server()
