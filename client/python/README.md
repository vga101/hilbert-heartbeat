# Python 3 clients

The clients in this directory implement the [Hilbert heartbeat base protocol](../../README.md), but also the additional status queries supported by the [Python 3 server](../../server). The different files contain:
- [`heartbeat.py`](heartbeat.py): The heartbeat client library and a console demo application.
- [`test.py`](test.py): A simplistic heartbeat test client that utilizes [`heartbeat.py`](heartbeat.py) (needs to be in the same directory).
- [`check_heartbeat.py`](check_heartbeat.py): A simplistic and standalone status query test client that is compatible with the [Python 3 server](../../server).

## Command line usage
All test clients can be run through the `python3` interpreter. They can pick up `HB_URL` respectively `HB_HOST` and `HB_PORT` from the environment to connect to the heartbeat server, e.g.
```
HB_HOST=localhost HB_PORT=8888 python3 heartbeat.py # or test.py or check_heartbeat.py
```
Note that `HB_HOST=localhost` and `HB_PORT=8888` are actually the default values.

## Library usage

[`heartbeat.py`](heartbeat.py) can act as a Python library.

### Settings:

* `heartbeat.HB_URL`: HB server connection URL (default is `127.0.0.1:8888`)
* `heartbeat.APP_ID`: Application ID (default is 'python_heartbeat_client_demo')

### Functions:

* `heartbeat.hb_init(timeout [,errorReturnValue])`: send `HB_INIT` message to HB server (with specified `timeout`).
* `heartbeat.hb_ping(timeout [,errorReturnValue])`: send `HB_PING` message to HB server (with specified `timeout`).
* `heartbeat.hb_done([timeout, [errorReturnValue]])`: send `HB_DONE` message to HB server (with specified `timeout` or with `0` by default).

Additionally, this client library provides extended functionality to communicate with the [Python 3 server](../../server):

* low-level communication (sending HTTP requests):
  * `heartbeat.hb_http_get(path [,errorReturnValue])`: send an `HTTP GET` request (with specified path) to HTTP server specified by global `HB_URL` setting.
  * `heartbeat.hb_http_post(path, data [,errorReturnValue])`: send an `HTTP POST` request (with specified path, incl. data) to HTTP server specified by global `HB_URL` setting.
* additional query functionality of the current heartbeat server:
  * `heartbeat.hb_list([errorReturnValue])`: query the heartbeat server to get a list of currently tracked client application IDs
  * `heartbeat.hb_status([ID [,errorReturnValue]])`: query the heartbeat server to get a status of a the host (or of the sepcified application)

#### Handling of a networking error
The error will be logged, and if `errorReturnValue` was not specified: an exception will be sent, 
otherwise `errorReturnValue` will be returned in case of an error.
