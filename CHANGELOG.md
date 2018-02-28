# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- General and API documentation
- Protocol:
  - support for `HTTP` `POST` requests
- Bash client:
  - add support for sending HTTP POST (in addition to existing HTTP GET)
  - add `cache_buster` into request string
  - wrappers for all heartbeat commands
  - wrappers for all heartbeat-query
  - test sample and query check
- Python client:
  - add support for sending HTTP POST (in addition to existing HTTP GET)
  - add `cache_buster` into request string
  - test sample and query check
  - handler for `Ctrl-C`
- JavaScript client:
  - public API to send heartbeats explicitly
  - zero interval disables automatic heartbeats

### Changed
- Directory structure of project repository
- Protocol:
  - `TIMEOUT` unit is now milliseconds
- Bash client:
  - improved settings handling (e.g. `HB_URL`, `APP_ID`)
  - single multi-purpose script (similar to busybox) - also useable as a library
  - switched to using `wget` (with `curl` as a fallback) internally
  - `hb_wrapper.sh`: wrapper for sending (customizable) HB init/done resp. before/after running some application in background
  - `hb_dummy.sh`: wrapper for sending (customizable) HB init/pings/done resp. before/while/after running some application in background
- JavaScript client:
  - use protocol of containing website by default (`//` instead of `http://`)
  - requests time out after a couple of seconds
  - cancel pending asynchronous requests before sending synchronous request
- Separation of Python server and client
- HB server
  - improved settings handling (e.g. `HB_URL`, `APP_ID`)
  - switched to Python 3
  - internal rewrite to improve stability, add more code structure and avoid using Timers
  - status reporting now have an overdue ratio instead of a simple counter + adjustable thresholds
  - suport for POST requests (equally to GET)
- Python client:
  - improved settings handling (e.g. `HB_URL`, `APP_ID`)
  - switched to Python 3
  - also useable as a library

### Deprecated

### Removed
- Python 2.x support
- Outdated scripts and examples

### Fixed
- JavaScript client:
  - broken initialization after delayed loading
- Python server:
  - empty status message on first app delay

### Security

## [0.2.0] - 2017-04-18
### Added
- Merging original scattered Gists
- Changelog according to [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
- Apache v2 license

### Changed
- Split [`malex984/dockapp`](https://github.com/malex984/dockapp) into [`hilbert/hilbert-*`](https://github.com/hilbert)
- Git branching model

### Fixed 
- Heartbeat Server for Python 3

### Security 
- Started to remove `sudo` and `privileged` requirements 

## [0.1.0] - 2016-09-02
### Added
- Monitoring server and agents
- Heartbeat server 
- Heartbeat wrappers and clients in Bash and JavaScript
- Integration of monitoring server (OMD) with dashboard's back-end server via MKLiveStatus
- First working system prototype using manual configurations

[Unreleased]: https://github.com/hilbert/hilbert-heartbeat/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/hilbert/hilbert-heartbeat/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/hilbert/hilbert-heartbeat/compare/v0.0.0...v0.1.0
