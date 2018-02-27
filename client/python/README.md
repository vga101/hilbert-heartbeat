# Client interaction with the prototype HB server using Python

**NOTE**: here under Python we mean Python 3

## Client HB library in Python

[heartbeat.py](heartbeat.py) is a library for interacting with HB server. As a library it povides the following functionality:

### Settings:

* `heartbeat.HB_URL`: HB server connection URL (default is `127.0.0.1:8888`)
* `heartbeat.APP_ID`: Application ID (default is 'python_heartbeat_client_demo')

### Functions:

* `heartbeat.hb_init(timeout [,errorReturnValue])`: send `HB_INIT` message to HB server (with specified `timeout`).
* `heartbeat.hb_ping(timeout [,errorReturnValue])`: send `HB_PING` message to HB server (with specified `timeout`).
* `heartbeat.hb_done([timeout, [errorReturnValue]])`: send `HB_DONE` message to HB server (with specified `timeout` or with `0` by default).

Additionally this client library provides extended functionality to communicate with the current HB server:

* low-level communication (sending HTTP requests):
  * `heartbeat.hb_read(path [,errorReturnValue])`: send an HTTP GET request (with specified path) to HTTP server specified by global HB_URL setting.
  * `heartbeat.hb_post(path, data [,errorReturnValue])`: send an HTTP POST request (with specified path, incl. data) to HTTP server specified by global HB_URL setting.
* additional query functionality of the current HB server:
  * `heartbeat.hb_list([errorReturnValue])`: query the HB Server to get a list of currently tracked client application IDs
  * `heartbeat.hb_status([ID [,errorReturnValue]])`: query the HB Server to get a status of a the host (or of the sepcified application)


**NOTE** about handling of a networking error by all above functions:
the error will be logged, and if `errorReturnValue` was not specified: an exception will be sent, 
otherwise `errorReturnValue` will be returned in case of an error.


### Library usage examples:
* [Basic HB test using heartbeat client library](test.py). It can be run directly (e.g. with `python3 test.py`). This sample requires `heartbeat.py` to be in the same directory.
* [heartbeat.py](heartbeat.py) also contains a command-line demo application, which communicates with HB server and logs the interactions to console. It can be run directly (e.g. with `python3 heartbeat.py`)


## Additional standalone host HB status query in Python

Sample query is in [check_heartbeat.py](check_heartbeat.py). 
It can be run directly (e.g. with `python3 check_heartbeat.py`). 
This query check is independent from the above client HB library.
