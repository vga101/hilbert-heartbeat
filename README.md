# Current Heartbeat design

We set HB server default port be **8888**.
Moreover for simplicity we assume that **HB Server runs on the client host and serves a single client host**.
Therefore `HB_URL = http://localhost:8888` for any client application.

ps: the current prototype `server/heartbeat2.py` contains:
* HB Server, which can be started with: python2 heartbeat2.py -s (any argument)
* HB Client testing application, which can be started with: python2 heartbeat2.py (no arguments)

NOTE: currently both HB Server and HB Client are to be run on a same host
(i.e. localhost is used everywhere) only due to HB Server interaction with the monitoring agent.

All HB-Client communications are HTTP-GET-Request at `HB_URL + "/" + HB_COMMAND + "?" + string(T) + "&appid=" + APP_ID`
 
NOTE: 
* `T` is the client's expected delay, `APP_ID` is a unique client application ID
* The server responds with the maximum time it is going to wait 
* `HB_COMMAND` is `hb_init` or `hb_ping or `hb_done` as follows:
  * Setup/Initialization: `HB_COMMAND = hb_init`. To be used by client-application-starter. 
    NOTE: the initial delay `T` may be elevated in order to account for the client-application initial startup & initialization.
  * Regular Heartbeat ping/pong: `HB_COMMAND = hb_ping`. To be sent from within client-application' main loop.  
  * Application closing: `HB_COMMAND = hb_done`. Last communication from application to HB Server. 
    NOTE: delay has no special meaning here.


![Protocol Sequence Diagram:](https://www.websequencediagrams.com/cgi-bin/cdraw?lz=dGl0bGUgSGVhcnRiZWF0IFByb3RvY29sCgpwYXJ0aWNpcGFudCAiTmFnaW9zIEFnZW50IgAND0hCIFNlcnZlciIKCm5vdGUgb3ZlcgAKDVN0YXJ0cyBvbiBjbGllbnQKYmVmb3JlIGFueSBBUFAgb3IKc3RhdHVzIHF1ZXJ5CmVuZCBub3RlCgB3DwBDBQBjBQpsb29wIEhCIFMAMgZRdWVyeWluZwoAgRwOLT4rAIEtDjogY2hlY2tfZG9ja2FwcF9oAIFxCC5zaAApEwCBUQo6IACBHAYoKQoAgWYLLS0-LQBREG5vX2FwcF8AgUsGAIEAEAAPIWVuZAoKCgCBYQktPisAgW0JAH4FcnQgQVBQAAkZZ2VuZXJhdGVfQVBQX0lEKCkAQAstPi0AQQsAGwYAXA8AgWQMaGJfaW5pdChpbml0X2RlbGF5LAAuBykgAIFzEQCBGgptYXgAMwUALQYAgg2BHEFQUACCfCoAIgsAgx4FAIMXCyoiQVBQAIMWCF9hcHAoAIJ3BiwAgX0PKQoKACUFLT4rACsHbWFpbl9sb29wAIVJB0FQUAAPBSAADgYAJQkAgwgPcGluZygAgwQOAIUEEQBZCHgAgzUGXwCGbAZfbmV4dAA7BQCBQIFZAIMYBgCCYwUAgX4KcXVpdAoKAII4GmRvbmUAgy8HAIIzGEdvb2QgYnllIQBUCgCGQA4gaXMgZmluaXNoZWQKCmRlc3Ryb3kgAIQXBQCHRQwAhngOZG9uZSB3aXRoAIdQBgCHeYFd&s=modern-blue)



# Heartbeat protocol implementations:
 * [Server (in python 2)](server/heartbeat2.py)
 * [BASH helpers, wrappers and samples](client/bash/)
 * [C Sample (based on BASH samples)](https://github.com/malex984/appchoo/commit/c0e1701d415b0eafc405c894f62a11131d11f06d)
 * [JS library (with asynchronous HTTP requests in JS)](client/web/hilbert-heartbeat.js)



# Original Heartbeat design

## Heartbeat brainstorming:
 * WebGL: add to render loop (initiate)
 * multi-thread / asynchron sending (should not block the application)
 * non-blocking i/o
 * how often: 1 beat per second (or less)?
 * `TCP/IP` connection: leave open?
 * `GET` request sending: add into URL "ID exhibit, heartbeat expectation" (selbstverpflichtung) => The server knows the IP (computer).
 * initial setup for monitoring software (also list of programs which run on which host)
   * startup via Nagios?
 * maintenance mode could be added (you put station on maintenance), if a station is not expected to be running (in order to avoid automatic restart during maintenance)

## Heartbeat protocol:
 * pass protocol parameters into container via ENVIRONMENT VARIABLES, e.g. `HB_URL=http://HB_HOST:HB_PORT/heartbeat.html?container=pong&next=%n`:
   * application substitutes %n with minimal time until next heartbeart	(milliseconds) and sends GET request
   * server answers with maximal time for next heartbeart (>minimal heartbeat time) (otherwise it will take some action)
 * ENVIRONMENT PARAMETERS are passed by url parameters into browser based applications some API exposed by electron for kiosk applications?
 * CLIENT: send minimal time until next heartbeat (ms)
 * SERVER: send maximal time until next heartbeat (ms)
 * when container is starting, the management system is waiting for some predefined time (15 seconds? same as regular waiting time when the app is running properly) before expecting the first heartbeat; afterwards the protocol is self tuning


## License
This project is licensed under the [Apache v2 license](LICENSE). See also [Notice](NOTICE).

