# Hilbert heartbeat

This repository contains the protocol definition and implementations of notification based health-check mechanism, subsequently called heartbeat.

## HTTP Protocol
The system consists of a HTTP client that sends heartbeat notifications and a HTTP server thats keeps track of these notifications and possible delays.

After an application registers at the heartbeat server, it is supposed to send periodic heartbeats until it deregisters (to be deliberately stopped). If the heartbeats are not sent in time, the application is considered to be in a defective state by the heartbeat server which in turn may forward this information to a higher-level monitoring system. The time until the next heartbeat is supposed to be send is configurable in each request.

### REST API
The server must accepts three different commands via `HTTP` `GET`: 
* `/hb_init?TIMEOUT&appid=APPLICATION_ID`: Register an application.  
  * Parameters:
    * `TIMEOUT` [ms]: The supplied value should account for application startup and initialization. The server must not consider the application delayed before this timeout.
    * `APPLICATION_ID` [string]: The application ID to register.
  * Response:
    * [ms]: The actual timeout used by the server. Must be >= `TIMEOUT`.
* `/hb_ping?TIMEOUT&appid=APPLICATION_ID`: Send a heartbeat.  
  * Parameters:
    * `TIMEOUT` [ms]: The value should generally be the same during application lifetime, but may be adjusted temporarily to account for long running computations. The server must not consider the application delayed before this timeout.
    * `APPLICATION_ID` [string]: The application ID this ping belongs to.
  * Response:
    * [ms]: The actual timeout used by the server. Must be >= `TIMEOUT`.
* `/hb_done?TIMEOUT&appid=APPLICATION_ID`: Deregister an application. Further heartbeats must not be sent for this application afterwards.  
  * Parameters:
    * `TIMEOUT` [ms]: Time until the application is supposed to have shutdown completely.
    * `APPLICATION_ID` [string]: The application ID to deregister.
  * Response:
    * [string]: Arbitrary goodbye message.

The server must accept the same requests via `POST` as well to account for certain limitations in the way client libraries work. In this case, no response needs to send by the server.

Additional query parameters are irgnored. This way you can e.g. bypass browser cache by adding a `cache_buster=TIMESTAMP` parameter that uses a unique `TIMESTAMP` for each request.

### Sequence diagram

![Protocol Sequence Diagram:](https://www.websequencediagrams.com/cgi-bin/cdraw?lz=dGl0bGUgSGVhcnRiZWF0IFByb3RvY29sCgpwYXJ0aWNpcGFudCAiSEIgU2VydmVyIgoACw9TdGFydAASBgoABAktPisAEAk6IHN0YXJ0IEFQUAAJGWdlbmVyYXRlX0FQUF9JRCgpAEALLT4tAEELABsGAFwPAIEUCjogaGJfaW5pdChpbml0X2RlbGF5LAAuBykgCgCBPQsASQ9tYXgAMwUALQYAgT4OKiJBUFAAgUAIX2FwcCgAgSEGLAAnDykKCgAlBS0-KwArB21haW5fbG9vcAoKbG9vcCBBUFAADwUgAA4GACUJAIEyD3BpbmcoAIEuDgCBKhEAWQh4AIFfBl9iZWZvcmVfbmV4dAA7BQoKZW5kAIEJCAAnCnF1aXQAgyYFAGQXZG9uZQCBWAcAXBhHb29kIGJ5ZSEAVAoAgxMOIGlzIGZpbmlzaGVkCgpkZXN0cm95IACCQAUAhBgMAINLDmRvbmUgd2l0aACEIwYK&s=earth)

The source of the sequence diagram can be found [here](https://www.websequencediagrams.com/?lz=dGl0bGUgSGVhcnRiZWF0IFByb3RvY29sCgpwYXJ0aWNpcGFudCAiSEIgU2VydmVyIgoACw9TdGFydAASBgoABAktPisAEAk6IHN0YXJ0IEFQUAAJGWdlbmVyYXRlX0FQUF9JRCgpAEALLT4tAEELABsGAFwPAIEUCjogaGJfaW5pdChpbml0X2RlbGF5LAAuBykgCgCBPQsASQ9tYXgAMwUALQYAgT4OKiJBUFAAgUAIX2FwcCgAgSEGLAAnDykKCgAlBS0-KwArB21haW5fbG9vcAoKbG9vcCBBUFAADwUgAA4GACUJAIEyD3BpbmcoAIEuDgCBKhEAWQh4AIFfBl9iZWZvcmVfbmV4dAA7BQoKZW5kAIEJCAAnCnF1aXQAgyYFAGQXZG9uZQCBWAcAXBhHb29kIGJ5ZSEAVAoAgxMOIGlzIGZpbmlzaGVkCgpkZXN0cm95IACCQAUAhBgMAINLDmRvbmUgd2l0aACEIwYK&s=earth).

## Implementations

Clients:
 * [Python3](client/python/)
 * [BASH](client/bash/) (helper and wrapper scripts)
 * [JavaScript](client/js/)
 * [C using BASH helper script](https://github.com/malex984/appchoo/commit/c0e1701d415b0eafc405c894f62a11131d11f06d)

Server:
 * [Python3](server) (with extended monitoring API)

### Notes
 * Clients usually pick up `APP_ID`, `HB_HOST` and `HB_PORT` from the environment, URL parameters or whatever seems appropriate (please check the individual client documentation). Default values are:
   * `HB_HOST`: `localhost`
   * `HB_PORT`: `8888`
 * In practice, meaningful default `TIMEOUT` values for `hb_ping` are between 1000 and 5000 (1s to 5s).
 * Heartbeat servers may treat an `hb_ping` with unknown `APP_ID` as `hb_init`. 

### Current usage in Hilbert

 * The heartbeat server is running as part of `omd_agent` service, which also contains plugins for checking the system health, including querying the HB server for the current Health status of the currently running top application on the station. For example: [check_heartbeat.py](client/python/check_heartbeat.py)
 * Most heartbeat clients currently rely on the bash helper [`hb_wrapper.sh`](client/bash/hb_wrapper.sh) to send `hb_init` and `hb_done` before starting the actual application resp. when application is about to stop (e.g. some exit signal was emitted).
 * currently, server and client are to be run on the same host (i.e. localhost is used everywhere) only due to the interaction of the heartbeat server with the monitoring agent.


## License
All code is this project is subject to the [Apache v2 license](LICENSE).
