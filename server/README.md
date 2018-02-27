# Heartbeat server

This Python3 program implements the server side of the heartbeat protocol. In addition, it provides an [extended API](#Extended-API) to allow other monitoring systems, such as Nagios/Check_mk, to query accumulated information about known clients.

## Usage
```
python3 heartbeat.py
```

## Main API
See the [protocol definition](../README.md).

## Extended API
The following `HTTP` `GET` queries are supported in addition to the [main protocol](../README.md):

 * `/list`: response will contain a list of `APP_ID`s for currently active applications
 * `/status`: general host status: there should be a single application
 * `/status?0&appid=APP_ID`: heartbeat status of specified application. The response format is compatible with Nagios.

### Example session
Assume the server is running on `localost:8888`. Let's list the connected apps:
```Bash
$ curl http://localhost:8888/list
Tetris
```
Now that we know there is a single app. Let's check its status:
```
$ curl http://localhost:8888/status
OK - fine application [Tetris]| od=1.83;3;5;0;6 delay=2725ms;;;
```
All good. What happends if more then one client is connected?
```Bash
$ curl http://localhost:8888/list
Sonic,
Zelda,
Tetris
$ curl http://localhost:8888/status
WARNING - multiple (3) applications: [Tetris,Zelda,Sonic]
```
Better just ask for a specific app then:
```
$ curl http://localhost:8888/status?appid=Zelda
OK - fine application [Zelda]| od=2.15;3;5;0;6 delay=2754ms;;;
```
This happens if a client doesn't send heartbeats anymore (without properly disconnecting via `hb_done`):
```
$ curl http://localhost:8888/status?appid=Tetris
WARNING - somewhat late application [Tetris]| od=3.83;3;5;0;6 delay=2850ms;;;
$ curl http://localhost:8888/status?appid=Tetris
CRITICAL - quite late application [Tetris]| od=5.07;3;5;0;6 delay=2850ms;;;
$ curl http://localhost:8888/status?appid=Tetris
CRITICAL - no application record for queried ID: [Tetris]
```

### Code examples
 * [check_heartbeat.py](../client/python/check_heartbeat.py)
 * [function `check_hilbert_heartbeat` from `check_hilbert.sh`](https://github.com/hilbert/hilbert-docker-images/blob/devel/images/omd_agent/check_hilbert.sh)
 * [client library in Python3](../client/python/)
 * [client helpers in BASH](../client/bash/)

## Sequence diagram
![HB Server Status Query Sequence Diagram:](https://www.websequencediagrams.com/cgi-bin/cdraw?lz=dGl0bGUgSGVhcnRiZWF0IFByb3RvY29sCgpwYXJ0aWNpcGFudCAiTmFnaW9zIEFnZW50IgAND0hCIFNlcnZlciIKCm5vdGUgb3ZlcgAKDVN0YXJ0cyBvbiBjbGllbnQKYmVmb3JlIGFueSBBUFAgb3IKc3RhdHVzIHF1ZXJ5CmVuZCBub3RlCgB3DwBDBQBjBQpsb29wIEhCIFMAMgZRdWVyeWluZwoAgRwOLT4rAIEtDjogY2hlY2tfaACBaQguc2gAIRMAgUkKOiAAgRQGKCkKAIFeCy0tPi0ASRBub19hcHBfAIFDBgB4EAAPIWVuZAoKCgCBWQktPisAgWUJAH4FcnQgQVBQAAkZZ2VuZXJhdGVfQVBQX0lEKCkAQAstPi0AQQsAGwYAXA8AgWQMaGJfaW5pdChpbml0X2RlbGF5LAAuBykgAIFzEQCBGgptYXgAMwUALQYAgg2BFEFQUACCdCoAIgsAgxYFAIMPCyoiQVBQAIMOCF9hcHAoAIJvBiwAgXUPKQoKACUFLT4rACsHbWFpbl9sb29wAIU5B0FQUAAPBSAADgYAJQkAgwAPcGluZygAgnwOAIR8EQBZCHgAgy0GXwCGXAZfbmV4dAA7BQCBQIFRAIMQBgCCWwUAgXYKcXVpdAoKAIIwGmRvbmUAgycHAIIrGEdvb2QgYnllIQBUCgCGMA4gaXMgZmluaXNoZWQKCmRlc3Ryb3kgAIQPBQCHNQwAhmgOZG9uZSB3aXRoAIdABgCHaIFW&s=earth)

The source of the sequence diagram can be found [here](https://www.websequencediagrams.com/?lz=dGl0bGUgSGVhcnRiZWF0IFByb3RvY29sCgpwYXJ0aWNpcGFudCAiTmFnaW9zIEFnZW50IgAND0hCIFNlcnZlciIKCm5vdGUgb3ZlcgAKDVN0YXJ0cyBvbiBjbGllbnQKYmVmb3JlIGFueSBBUFAgb3IKc3RhdHVzIHF1ZXJ5CmVuZCBub3RlCgB3DwBDBQBjBQpsb29wIEhCIFMAMgZRdWVyeWluZwoAgRwOLT4rAIEtDjogY2hlY2tfaACBaQguc2gAIRMAgUkKOiAAgRQGKCkKAIFeCy0tPi0ASRBub19hcHBfAIFDBgB4EAAPIWVuZAoKCgCBWQktPisAgWUJAH4FcnQgQVBQAAkZZ2VuZXJhdGVfQVBQX0lEKCkAQAstPi0AQQsAGwYAXA8AgWQMaGJfaW5pdChpbml0X2RlbGF5LAAuBykgAIFzEQCBGgptYXgAMwUALQYAgg2BFEFQUACCdCoAIgsAgxYFAIMPCyoiQVBQAIMOCF9hcHAoAIJvBiwAgXUPKQoKACUFLT4rACsHbWFpbl9sb29wAIU5B0FQUAAPBSAADgYAJQkAgwAPcGluZygAgnwOAIR8EQBZCHgAgy0GXwCGXAZfbmV4dAA7BQCBQIFRAIMQBgCCWwUAgXYKcXVpdAoKAIIwGmRvbmUAgycHAIIrGEdvb2QgYnllIQBUCgCGMA4gaXMgZmluaXNoZWQKCmRlc3Ryb3kgAIQPBQCHNQwAhmgOZG9uZSB3aXRoAIdABgCHaIFW&s=earth).
