# Current Heartbeat Protocol design

NOTE: in what follows **HB** stays for **Heartbeat**.

## General HB principle:

![Protocol Sequence Diagram:](https://www.websequencediagrams.com/cgi-bin/cdraw?lz=dGl0bGUgSGVhcnRiZWF0IFByb3RvY29sCgpwYXJ0aWNpcGFudCAiSEIgU2VydmVyIgoACw9TdGFydAASBgoABAktPisAEAk6IHN0YXJ0IEFQUAAJGWdlbmVyYXRlX0FQUF9JRCgpAEALLT4tAEELABsGAFwPAIEUCjogaGJfaW5pdChpbml0X2RlbGF5LAAuBykgCgCBPQsASQ9tYXgAMwUALQYAgT4OKiJBUFAAgUAIX2FwcCgAgSEGLAAnDykKCgAlBS0-KwArB21haW5fbG9vcAoKbG9vcCBBUFAADwUgAA4GACUJAIEyD3BpbmcoAIEuDgCBKhEAWQh4AIFfBl9iZWZvcmVfbmV4dAA7BQoKZW5kAIEJCAAnCnF1aXQAgyYFAGQXZG9uZQCBWAcAXBhHb29kIGJ5ZSEAVAoAgxMOIGlzIGZpbmlzaGVkCgpkZXN0cm95IACCQAUAhBgMAINLDmRvbmUgd2l0aACEIwYK&s=earth)

## Implementation details

Currently HB Server is a synchronous HTTP server.
We set its default port to be **8888**.
For simplicity let us assume here that HB Server runs together
with the Client Application on the same host.
Then `HB_URL = http://127.0.0.1:8888` for any client application running on the host.

HB Clients are expected to send HTTP-GET (or HTTP-POST) requests to the following URL:
`HB_URL + "/" + HB_COMMAND + "?" + string(TIMEOUT) + "&appid=" + APPLICATION_ID`.
Note that sending HB messages should not block an application.
 
NOTE: 
* `TIMEOUT` is the expected client's timeout before the next HB message (integer number of [ms]),
* `APPLICATION_ID` is a unique client application ID
* The server responds with the maximum interval (integer number of [ms])  it is going to wait before declaring that Application is too late
* `HB_COMMAND` can be `hb_init` or `hb_ping or `hb_done`. Their usage is as follows:
  * Setup/Initialization: `HB_COMMAND = hb_init`. To be used by client-application-starter. 
    NOTE: the initial delay `TIMEOUT` may be elevated in order to account for the client-application initial startup & initialization.
  * Regular HB ping/pong: `HB_COMMAND = hb_ping`. To be sent from within client-application' main event-handling loop.
    NOTES:
    * CLIENT: sends the minimal time interval until next HB (in [ms])
    * SERVER: responds with the maximal time interval until next HB (in [ms])
    * in practice one ping in ~5 seconds seems to be enough.
  * Application closing: `HB_COMMAND = hb_done`. Last communication from finishing application to HB Server.
    NOTE: delay has no special meaning here. The HB Server response can be arbitrary Goodbye text.

NOTE: initial `hb_init` can currently also be replaced with `hb_ping`.
This means that a minimal client can be restricted to only send `hb_ping` messages while it is running.

Note: HB Server and Clients are encouraged to obtain HB protocol parameters from ENVIRONMENT VARIABLES, e.g. `APP_ID`, `HB_PORT`, `HB_HOST` or `HB_URL`.
`HB_URL` should be in sync with `HB_PORT` and/or `HB_HOST` if they are specified.



## HB protocol implementations/samples:

Sample Clients:
 * [Sample Client in Python3](client/python/)
 * [helpers, wrappers in BASH](client/bash/)
 * [JS library (with asynchronous HTTP requests in JS)](client/js/). Note: HB protocol parameters may be added into the URL.
 * [Example in C using helper in BASH](https://github.com/malex984/appchoo/commit/c0e1701d415b0eafc405c894f62a11131d11f06d)

Server prototype:
 * [HB Server](server) (currently runs using python 3)

## Current HB usage in Hilbert

 * HB Server is running as part of `omd_agent` service, which also contains plugins for checking the system health,
   including querying the HB server for the current Health status of the currently running top application on the station.
   For example: [check_heartbeat.py](server/check_heartbeat.py)
 * HB Clients currently rely on the bash helper [`hb_wrapper.sh`](client/bash/hb_wrapper.sh) to send `hb_init` and `hb_done`
 before starting the actual application
 resp. when application is about to stop (e.g. some exit signal was emitted).

NOTE: currently both HB Server and HB Client are to be run on a same host
(i.e. localhost is used everywhere) only due to HB Server interaction with the monitoring agent.

## License
This project is licensed under the [Apache v2 license](LICENSE). See also [Notice](NOTICE).
