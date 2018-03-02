# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- General and API documentation
- Protocol and implementations:
  - support for `HTTP POST` requests
- All clients:
  - bypass caches by adding a `cache_buster` into the query string
- Bash client:
  - wrappers for all heartbeat commands and monitoring query
  - `hb_dummy.sh`: sends fake heartbeats for a applications that doesn't support it
  - `hb_wrapper.sh`: like `hb_dummy.sh`, but sends only `hb_ping` and `hb_done`
  - example scripts for heartbeat and monitoring
- Python client:
  - handler for `Ctrl-C`
  - example scripts for heartbeat and monitoring
- JavaScript client:
  - public API to send heartbeats explicitly
  - zero interval disables automatic heartbeats

### Changed
- Directory structure of project repository
- Protocol and implementations:
  - `TIMEOUT` unit is now milliseconds
- Bash client:
  - improved settings handling (e.g. `HB_URL`, `APP_ID`)
  - single multi-purpose script (similar to busybox) - also useable as a library
  - switched to using `wget` (with `curl` as a fallback) internally
- JavaScript client:
  - use protocol of containing website by default (`//` instead of `http://`)
  - requests time out after a couple of seconds
  - cancel pending asynchronous requests before sending synchronous request
- Separation of Python server and client
- Server
  - improved settings handling (e.g. `HB_URL`, `APP_ID`)
  - status reporting now has an overdue ratio instead of a simple counter + adjustable thresholds
- Python client:
  - improved settings handling (e.g. `HB_URL`, `APP_ID`)
  - also usable as a library

### Removed
- Python 2.x support
- Outdated scripts and examples

### Fixed
- JavaScript client:
  - broken initialization after delayed loading
- Python server:
  - empty status message on first app delay
  - stability problems related to `Timer`s

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
