#! /usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote

from time import time
import os  # environment vars

PORT_NUMBER = int(os.getenv('HB_PORT', 8888))
HOST_NAME = os.getenv('HB_HOST', '127.0.0.1')
HB_SERVER_URL = os.getenv('HB_URL', "http://" + HOST_NAME + ":" + str(PORT_NUMBER))

visits = {} ### { ID => (StartTime, Timeout, ?TimerObject?, OverdueCounter) }

# TODO: add better logging?

# def toolate(ID):
#     ts = time()
#     print("[", ts, "] [", ID, "]: ", visits[ID])
#
#     d = visits[ID]
#     # Collect statistics about ID
#
#     if d[3] > 6:
#         print("TOO overdue - dropping!!!")  # TODO: early detection of overdue clients!!???
#         del visits[ID]
#     else:
#         visits[ID] = (d[0], d[1], None, d[3] + 1) # Timer(d[1], toolate, [ID])
# #        visits[ID][2].start()  # Another Chance???

def clear_overdue_visits():
    global visits
    # NOTE: no need to lock the global dictionary `visits` since HB server runs synchronously!
    tmp = {}
    ts = time()
    while visits:
        kv = visits.popitem()
        ID = kv[0]
        assert ID not in visits

        d  = kv[1]
        delta = float(ts - d[0])/float(d[1])
        if delta > 6.0:
            print("TOO overdue - dropping: ")  # TODO: early detection of overdue clients!!???
            print("[", ts, "] [", ID, "]: ", d)
#            del visits[ID]
        else:
            tmp[ID] = (d[0], d[1], d[2], int(delta)) # Timer(d[1], toolate, [ID])
#            visits[ID][2].start()  # Another Chance???
    assert not visits
    visits = tmp


class MyHandler(BaseHTTPRequestHandler):
    def status(s, ID=None):
        """
        # query the status of currently tracked visits (compatible with OMD)
        """
        if (ID is None) and (len(visits) == 1):
            ID = next(iter(visits.keys()))

        if ID is not None:
            if ID in visits:
                # s.status(ID)
                d = visits[ID]

                t = d[0] # start time
                dd = d[1] # timeout
                od = d[3] # current statistics

                assert (od >= 0)

                # see http://nagios-plugins.org/doc/guidelines.html
                app = "application [" + str(ID) + "]| od=" + str(od) + ";4;6;0;7 delay=" + str(dd) + ";;; "

                ## STATUS CODE???
                if od <= 3:
                    s.wfile.write(bytes("OK - fine " + app, 'UTF-8'))
                elif od <= 5:
                    s.wfile.write(bytes("WARNING - somewhat late " + app, 'UTF-8'))
                else:
                    s.wfile.write(bytes("CRITICAL - quite late " + app, 'UTF-8'))

            else:
                s.wfile.write(bytes("CRITICAL - no application record for queried ID: [" + str(ID) + ']', 'UTF-8'))
        else:
            if len(visits) > 1:
                s.wfile.write(bytes(
                    "WARNING - multiple (" + str(len(visits)) + ") applications: [{}]".format(','.join(visits.keys())),
                    'UTF-8'))
            elif len(visits) == 1:
                s.wfile.write(bytes("UNKNOWN - no heartbeat clients at the moment...", 'UTF-8'))


    def do_GET(s):
        global visits
        #        global overdue
        clear_overdue_visits()

        s.send_response(200)
        s.send_header('Content-type', 'text/html')
        s.send_header('Access-Control-Allow-Origin', '*')
        s.end_headers()

        # NOTE: URL "localhost:8888/hb_init?48.2&appid=test_client_python" should be parsed as follows:
        #         '/hb_init', '48.2', 'appid=test_client_python']
        ### TODO: FIXME: the following url parsing is neither failsafe nor secure! :-(

        # NOTE: PARSING: s.path as follows: path ? T & appid = ID [& ...] :
        path = unquote(s.path)

        if path.startswith("/list"):
            # NOTE: list currently tracked visits
            for k, v in visits.items():
                s.wfile.write(bytes(str(k) + "\n", 'UTF-8'))
            return

        tail = ''
        if path.find('?') >= 0:
            path, tail = path.split('?', maxsplit=1)

        assert not (tail.find('?') >= 0)

        query = tail.split('&')

        ID = None
        if (tail != "") and (len(query) > 0):
            for q in query:
                if q.startswith('appid='):
                    ID = q[6:]
                    break
        # ID = query[1].split('=')[1]  # + " @ " + s.client_address[0] # " || " + s.headers['User-Agent']
        # ID = query[0].split('=')[1]  # + " @ " + s.client_address[0] # " || " + s.headers['User-Agent']

#        print("Input request: [{}] -> cmd: [{}], query: {}, ID: [{}]".format(s.path, path, query, ID))

        if path.startswith("/status"):
            MyHandler.status(s, ID)
            return

#        if ID in visits:
#            print("PREVIOUS STATE", visits[ID])
#            visits[ID][2].cancel()  # !

        if len(query[0]) == 0:
            T = 0.0
        else:  # interval: floating number (in ms = 1/1000 s). Has to be converted into seconds
            T = float(query[0]) / 1000.0

        T = T + 1.0  # (T*17)/16 ? (T*11)/8) ?
        assert (T > 0.0)

        ts = time() # current time
        if (((path == "/hb_init") or (path == "/hb_ping")) and (ID not in visits)):
            # Hello little brother! Big Brother is watching you!
            print("Creation from scratch : ", ID, " at ", ts)
            visits[ID] = (ts, T, None, 0) # Timer(T, toolate, [ID])
            s.wfile.write(bytes(str(1000.0*T), 'UTF-8'))  # ?
#            visits[ID][2].start()

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
            visits[ID] = (ts, T, None, 0)  # NOTE: forget previous overdue! # Timer(T, toolate, [ID])
            s.wfile.write(bytes(str(1000.0*T), 'UTF-8'))
#            visits[ID][2].start()
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
