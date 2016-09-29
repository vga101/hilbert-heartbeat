# Current Heartbeat desing
 * https://gist.github.com/malex984/dbec16e9c7d88f295071

# Heartbeat protocol implementations:
 * Server (in python2): `server/heartbeat2.py`
 * BASH helpers, wrappers (and samples) are in `client/bash/`
 * C Sample (based on BASH samples): `https://github.com/malex984/appchoo/commit/c0e1701d415b0eafc405c894f62a11131d11f06d` 
 * JS library: `client/web/hilbert-heartbeat.js` (with asynchronous HTTP requests in JS)



# Original Heartbeat design

## Heartbeat brainstorming:
 * webgl: add to render loop (initiate)
 * multithread / asynchron sending (should not block the application)
 * non-blocking i/o
 * how often: 1 beat per second (or less)?
 * TCPIP connection: leave open?
 * GET request sending: add into URL "ID exhibit, heartbeat expectation" (selbstverpflichtung) => The server knows the IP (computer).
 * initial setup for monitoring software (also list of programs which run on which host)
   * startup via Nagios?
 * maintenance mode could be added (you put station on maintenance), if a station is not expected to be running (in order to avoid automatic restart during maintenance)

## Heartbeat protocol:
 * pass protocol parameters into container via ENVIRONMENT VARIABLES, e.g.
   * HB_URL=http://HB_HOST:HB_PORT/heartbeat.html?container=pong&next=%n
     * application substitutes %n with minimal time until next heartbeart	(milliseconds) and sends GET request
     * server answers with maximal time for next heartbeart (>minimal heartbeat time) (otherwise it will take some action)
   * HB_URL=tcp://HB_HOST:HB_PORT
 * ENVIRONMENT PARAMETERS are passed by url parameters into browser based applications some API exposed by electron for kiosk applications?
 * CLIENT: send minimal time until next heartbeat (ms)
 * SERVER: send maximal time until next heartbeat (ms)
 * when container is starting, the management system is waiting for some predefined time (15 seconds? same as regular waiting time when the app is running properly) before expecting the first heartbeat; afterwards the protocol is self tuning

