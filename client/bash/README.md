# Bash clients

The clients in this directory implement the [Hilbert heartbeat base protocol](../../README.md), but also the additional status queries supported by the [Python 3 server](../../server). The different files contain:
- [`heartbeat.sh`](heartbeat.sh): The heartbeat client library and an application entry point for other scripts.
- `hb*.sh`: Symlinks to [`heartbeat.sh`](heartbeat.sh) that trigger different actions based on the symlink name.
- [`test.sh`](test.sh): A simplistic heartbeat test client that utilizes the [`heartbeat.sh`](heartbeat.sh) library (needs to be in the same directory).
- [`check_heartbeat.sh`](check_heartbeat.sh): A simplistic and standalone status query test client that is compatible with the [Python 3 server](../../server).

## Dependencies
The scripts require at least Bash 4 as well as either `wget` or `curl` in the `PATH`.

## Settings

All scripts recognize certain environment variables:
- `HB_HOST`: the hostname/IP of the heartbeat server (default: `127.0.0.1`)
- `HB_PORT`: the port of the heartbeat server (default: `8888`)
- `HB_URL`: combined host, port and protocol (default: `http://HB_HOST:HB_PORT`)

Most of the scripts also accept
- `APP_ID`: the application ID (default: none)

## Command line usage

### Single heartbeat commands

- `APP_ID=appid ./hb_init.sh timeout`: Send a `hb_init` command with given `timeout` [ms] via `HTTP POST`
- `APP_ID=appid ./hb_ping.sh timeout`: Send a `hb_ping` command with given `timeout` [ms]  via `HTTP GET`
- `APP_ID=appid ./hb_done.sh timeout`: Send a `hb_done` command with given `timeout` [ms]  via `HTTP POST`
- `APP_ID=appid ./hb.sh cmd timeout`: Send arbitrary commands with given `timeout` [ms] via `HTTP GET` **(deprecated)**

### Wrapper scripts

- `APP_ID=appid ./hb_wrapper.sh cmd [args]`: Launch `cmd` in the background, wait for it to exit and
  - if `HB_SEND_INIT=true`, send `hb_init` before `cmd` is executed
  - if `HB_SEND_PING=true`, send regular `hb_ping`s while `cmd` is running
  - if `HB_SEND_DONE=true`, send `hb_done` once `cmd` exited
- `APP_ID=appid hb_dummy.sh cmd [args]`: Equal to `APP_ID=appid HB_SEND_INIT=true HB_SEND_PING=true HB_SEND_DONE=true ./hb_wrapper.sh cmd [args]`.

### Monitoring

These extended commands only work with the [Python 3 server](../../server).

- `./hb_list.sh`: List all applications IDs currently monitored.
- `./hb_status.sh [appid]`: Retrieve detailed status information for an `appid` or for all known application IDs if `appid` is missing.

## Library usage

It is possible to use `heartbeat.sh` as a Bash library:
```
export HB_BASH_LIBRARY=1
source ./heartbeat.sh
```

#### High-level wrappers/helpers
Each of the `hb*.sh` command line tools has a corresponding function in `heartbeat.sh` that you can call directly in your script. `hb_init.sh` just calls the `hb_init` function with the same arguments ans so forth. 

#### Middle-level:
  * `_hb_init timeout`: send `HB_INIT` message with given timeout and handle the server response.
  * `_hb_ping timeout`: send `HB_PING` message with given timeout and handle the server response.
  * `_hb_done [timeout=0]`: send `HB_DONE` message with optionally given timeout and handle the server response.

#### Low-level:
  * `HB_SEND_MESSAGE cmd timeout`: send a generic heartbeat command (with specified `timeout`) via `HTTP GET`.
  * `HB_POST_MESSAGE cmd timeout`: send a generic heartbeat command (with specified `timeout`) via `HTTP POST`.
  * `HB_SEND_INIT timeout`: send `HB_INIT` message with given timeout.
  * `HB_SEND_PING timeout`: send `HB_PING` signal with given timeout.
  * `HB_SEND_DONE [timeout=0]`: send `HB_DONE` signal with given timeout.
