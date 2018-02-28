# Client interaction with the prototype HB server using pure BASH

**NOTE**: here under BASH we mean BASH >= 4

## Client HB library in BASH

[heartbeat.sh](heartbeat.sh) is a BASH library for interacting with HB server. As a library it povides the following functionality:

**NOTE**:
 * networking errors will be detected in low-level functions and corresponding (non-zero) exit code is returned. High-level functions and helpers also print an OK message with the server response to STDOUT or an ERROR message to STDERR.
 * all timeouts and intervals should be in [ms] = 1/1000 of a second


### Generic HB functionality:

**NOTE**: the following functions require `APP_ID` to be set.

#### Low-level:
  * `HB_SEND_MESSAGE cmd timeout`: send a generic HB command (with specified `timeout`) via HTTP GET
  * `HB_POST_MESSAGE cmd timeout`: send a generic HB command (with specified `timeout`) via HTTP POST
  * `HB_SEND_INIT timeout`: send `HB_INIT` message with given timeout to HB server
  * `HB_SEND_PING timeout`: send `HB_PING` signal with given timeout to HB server
  * `HB_SEND_DONE [timeout=0]`: send `HB_DONE` signal with given timeout to HB server

#### Middle-level:
  * `_hb_init timeout`: send `HB_INIT` message with given timeout and handle the server response
  * `_hb_ping timeout`: send `HB_PING` message with given timeout and handle the server response
  * `_hb_done [timeout=0]`: send `HB_DONE` message with optionally given timeout and handle the server response

#### High-level wrappers/helpers

**NOTE**: directly accesible from comman-line as separate tools via separate symbolic links.

  * `hb_init timeout`: send a single `HB_INIT` message to HB server (with specified `timeout`)
  * `hb_ping timeout`: send a single `HB_PING` message to HB server (with specified `timeout`)
  * `hb_done [timeout=0]`: send a single `HB_DONE` message to HB server (with specified `timeout` or with `0` by default)
  *  (**deprecated!) `hb cmd timeout`: send a generic HB command (with specified `timeout`) via HTTP GET. Please use high-level helpers/functions instead!
  * `hb_dummy _BG_APP_EXEC_LINE_`: make sure to send HB pings while specified application runs in BG.
  * `hb_wrapper _BG_APP_EXEC_LINE_`: can optionally send any of HB messages and wait in FG, while specified application is running in BG. Behaviour is controlled via a set of environment variables:
     * `HB_SEND_INIT`, `HB_SEND_PING`, `HB_SEND_DONE` boolean switches (`true`, `false`) for sending corresponding HB messages
     * `HB_INIT_TIMEOUT`, `HB_PING_INTERVAL`, `HB_DONE_TIMEOUT` - corresponding intervals/timeouts.

### High-level **query** functionality:
**NOTE**: directly accesible from comman-line as separate tools via separate symbolic links.

  * `hb_list`: Query HB server for current client IDs
  * `hb_status`: Query HB server for the host status or the status of individual client (if `APP_ID` is specified)

### Settings:

The following environment variables may be required in order to use the library:  
 * `APP_ID`: Application ID will NOT be set by default! It will be required for any functionality involving HB_INIT, HB_PING or HB_DONE! 
 * `HB_URL`: HB server connection URL (default is `127.0.0.1:8888`)


### Library usage examples:
* [Basic HB test using heartbeat client library](hb_test.sh). It can be run directly (e.g. with `./hb_test.sh`).
  This sample requires `heartbeat.sh` to be in the same directory.
* One can run any GUI application (e.g. a browser) with any command-line arguments using provided helpers (`hb_dummy.sh` and `hb_wrapper.sh`). For example: 
  `APP_ID=app ./hb_dummy.sh browser.sh <URL>` it is the same as 
  `APP_ID=app HB_SEND_INIT=true HB_SEND_PING=true HB_SEND_DONE=true ./hb_wrapper.sh browser.sh <URL>`


## Additional standalone host HB status query in BASH

Sample query is in [check_heartbeat.py](check_heartbeat.sh). 
It can be run directly (e.g. with `./check_heartbeat.sh`). 
This query check is independent from the above client HB library.
