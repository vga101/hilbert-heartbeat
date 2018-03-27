#! /usr/bin/env python3

from __future__ import absolute_import, print_function, unicode_literals

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote, urlparse

from time import time
import os  # environment vars
import sys

if "HB_URL" in os.environ:
    # NOTE: extract host and port from given URL. Should coincide with HB_PORT resp. HB_HOST if also set.
    HB_SERVER_URL = os.getenv('HB_URL')
    p = urlparse(HB_SERVER_URL)

    assert p.scheme == 'http' # we only support HTTP at the moment
    assert p.port is not None # port must be specified if HB_URL was set!
    assert p.hostname is not None

    PORT_NUMBER = int(p.port)
    HOST_NAME = p.hostname

    if 'HB_PORT' in os.environ:
        assert PORT_NUMBER == int(os.getenv('HB_PORT'))

    if 'HB_HOST' in os.environ:
        assert HOST_NAME == os.getenv('HB_HOST')
else:
    PORT_NUMBER = int(os.getenv('HB_PORT', 8888))
    HOST_NAME = os.getenv('HB_HOST', '127.0.0.1')

# Main data storage with all visit data
visits = {}  # { APP_ID => (0: StartTime, 1: Timeout, 2: OverdueCounterStatistic) }

WARN_THRESHOLD = 3
CRIT_THRESHOLD = 5
OVERDUE_THRESHOLD = 6


class HeartBeatHandler(BaseHTTPRequestHandler):

    def do_POST(s):
        """
        Delegate handling of POST requests to the shared request handler (server_request_handler)
        :return: nothing
        """
        s.server_request_handler("POST")

    def do_GET(s):
        """
        Delegate handling of POST requests to the shared request handler (server_request_handler)
        :return: nothing
        """
        s.server_request_handler("GET")

    def write_response(s, data):
        """
        Write any data into HTTP response
        :param s: HTTP server object
        :param data: any data
        :return: nothing
        """
        s.wfile.write(bytes("{}".format(data), 'UTF-8'))

    def write_response_headers(s, code=200):
        """
        Write response headers with some response code
        :param s: HTTP server object
        :param code: response code. 200 OK, 400 - bad request
        :return: nothing
        """
        s.send_response(code)
        s.send_header('Content-type', 'text/plain')  # /html?
        s.send_header('Access-Control-Allow-Origin', '*')
        s.end_headers()

    def clear_overdue_visits(s, ts):
        """
        Check all visits and

        :return: nothing
        """
        global visits

        # NOTE: no need to lock the global dictionary `visits` since HB server runs synchronously!
        tmp = {}
        while visits:  # while there are any visits:
            kv = visits.popitem()  # pop any visit

            ID = kv[0]
            assert ID not in visits

            d = kv[1]
            delta = float(ts - d[0]) / float(d[1])  # overdue calculation!
            if delta >= OVERDUE_THRESHOLD:
                s.log_message("[%s]: [%s] is too late (delta: %s) => dropping [%s]!", str(ts), ID, str(delta), str(d))
            else:
                tmp[ID] = (d[0], d[1], delta)

        assert not visits
        visits = tmp  # move visits back

    def write_status(s, ID=None):
        """
        query the status of currently tracked visit(s) (compatible with OMD) either about given visit or in general
        :param s: HTTP server object
        :param ID: optional client APP_ID
        :return: nothing
        """
        global visits

        if (ID is None) and (len(visits) == 1):
            ID = next(iter(visits.keys()))

        if ID is not None:
            if ID in visits:
                d = visits[ID]

                t = d[0]  # start time
                dd = d[1]  # timeout
                od = d[2]  # current statistics

                assert (od >= 0.0)

                # see http://nagios-plugins.org/doc/guidelines.html
                app = "application [{}]| od={:3.2f};{};{};0;{} delay={}ms;;; ".format(
                    ID, od, WARN_THRESHOLD, CRIT_THRESHOLD, OVERDUE_THRESHOLD, dd)

                # Figure out the status code for Nagios
                if od < WARN_THRESHOLD:
                    s.write_response("OK - fine " + app)
                elif od < CRIT_THRESHOLD:
                    s.write_response("WARNING - somewhat late " + app)
                else:
                    s.write_response("CRITICAL - quite late " + app)

            else:
                s.write_response("CRITICAL - no application record for queried ID: [" + str(ID) + ']')
        else:
            if len(visits) > 1:
                s.write_response("WARNING - multiple ({}) applications: [{}]".format(len(visits),
                                                                                      ','.join(visits.keys())))
            elif len(visits) == 0:
                s.write_response("UNKNOWN - no heartbeat clients at the moment...")

    def server_request_handler(s, httpRequestMethod):
        """
        Handle GET and POST HTTP Requests
        :param s:
        :return: nothing
        """
        ts = 1000 * time()  # current time in ms
        s.clear_overdue_visits(ts)

        path = unquote(s.path)

        # NOTE: PARSING: s.path as follows: path ? T & appid = ID [& ...] :
        # NOTE: URL "localhost:8888/hb_init?482&appid=test_client_python" should be parsed as follows:
        #         'hb_init', '482', 'appid=test_client_python']

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
                    ID = ID + " @ " + s.client_address[0]  # " || " + s.headers['User-Agent'] # for backward compatibility with monitoring-related tools!
                    break

        assert path[0] == '/'
        path = path.rsplit(sep='/', maxsplit=1)[1]

#        s.log_message("Method: {}, URL path parsing => cmd: [{}], ID: [{}], query: {}".format(httpRequestMethod, path, ID, query))

        global visits

        if path == "list":
            # NOTE: list currently tracked visits
            s.write_response_headers()
            for k, v in visits.items():
                s.write_response(str(k) + "\n")
            return

        if path == "status":
            s.write_response_headers()
            s.write_status(ID=ID)
            return

        if len(query[0]) == 0:  # What if the leading interval parameter is missing!?
            T = 0
        else:  # interval: floating number (in ms = 1/1000 s). Has to be converted into seconds
            T = int(query[0])

        T = T + 1000  # add a second to enable some tolerance
        # T is in ms!
        assert (T > 0)

        # Main logic:
        # If ID is already known: Actions are as follows:
        # init, ping => update its visit record
        # done => delete its visit record
        # If ID is currently unknown: Actions are as follows:
        # init, ping => create new visit record
        # done => nothing to do
        if path == "hb_done":  # Delete record for finished APP
            if ID in visits:
                s.log_message('[%s ms] Destruction of [%s]', str(ts), ID)
                del visits[ID]
            s.write_response_headers()
            s.write_response("So Long, and Thanks for All the Fish!")

        elif (((path == "hb_init") or (path == "hb_ping")) and (ID not in visits)):  # ADD NEW visit
            if path == "hb_ping":
                s.log_message('WARNING: application {} started with hb_ping instead of hb_init!'.format(ID))
            # Hello little brother! Big Brother is watching you!
            s.log_message('[%s ms] Construction of [%s]', str(ts), ID)
            visits[ID] = (ts, T, 0)
            s.write_response_headers()
            s.write_response(T)  # send PONG in ms

        elif (((path == "hb_ping") or (path == "hb_init")) and (ID in visits)): # UPDATE on subsequent PINGs
            if path == "hb_init":
                s.log_message('WARNING: application {} has beed already reported! It should not send hb_init after hb_ping or hb_init!'.format(ID))

            s.log_message('[%s ms] Update of [%s]', str(ts), ID)
            lastts = visits[ID][0]
            lastt = visits[ID][1]
            overdue = visits[ID][2]

            # NOTE: we currently just forget previous overdue statistics:
            visits[ID] = (ts, T, 0)

            s.write_response_headers()
            s.write_response(T)  # send PONG in ms

        else:
            s.log_error("Wrong request: [%s] with ID: [%s] and T: [%s]", s.path, ID, str(T))
            s.write_response_headers(code=400)
            s.write_response("ERROR: cannot process your request: [{}]".format(s.path))
        return


def test_server(HandlerClass=HeartBeatHandler, ServerClass=HTTPServer, protocol="HTTP/1.0"):
    """Test the HTTP request handler class.
    """

    server_address = (HOST_NAME, PORT_NUMBER)

    HandlerClass.protocol_version = protocol
    httpd = ServerClass(server_address, HandlerClass)

    sa = httpd.socket.getsockname()
    print("Serving HTTP on [{}], port: [{}]...".format(sa[0], sa[1]))
    httpd.serve_forever()


def main_exception_handler(type, value, tb):
    global visits

    print('-' * 40, file=sys.stderr)
    print('Uncaught exception! Type: {}, Value: {}'.format(type, value), file=sys.stderr)
    import traceback
    traceback.print_exc()  # XXX But this goes to stderr!
    print('Current visits: ', file=sys.stderr)
    for ID in visits:
        print('ID: [{}] => VISIT: [{}]'.format(ID, str(visits[ID])), file=sys.stderr)
    print('-' * 40, file=sys.stderr)


if __name__ == '__main__':
    sys.excepthook = main_exception_handler  # Install exception handler
    test_server()
