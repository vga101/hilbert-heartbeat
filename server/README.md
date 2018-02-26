# Sample Heartbeat Server implementation

![HB Server Status Query Sequence Diagram:](https://www.websequencediagrams.com/cgi-bin/cdraw?lz=dGl0bGUgSGVhcnRiZWF0IFByb3RvY29sCgpwYXJ0aWNpcGFudCAiTmFnaW9zIEFnZW50IgAND0hCIFNlcnZlciIKCm5vdGUgb3ZlcgAKDVN0YXJ0cyBvbiBjbGllbnQKYmVmb3JlIGFueSBBUFAgb3IKc3RhdHVzIHF1ZXJ5CmVuZCBub3RlCgB3DwBDBQBjBQpsb29wIEhCIFMAMgZRdWVyeWluZwoAgRwOLT4rAIEtDjogY2hlY2tfaACBaQguc2gAIRMAgUkKOiAAgRQGKCkKAIFeCy0tPi0ASRBub19hcHBfAIFDBgB4EAAPIWVuZAoKCgCBWQktPisAgWUJAH4FcnQgQVBQAAkZZ2VuZXJhdGVfQVBQX0lEKCkAQAstPi0AQQsAGwYAXA8AgWQMaGJfaW5pdChpbml0X2RlbGF5LAAuBykgAIFzEQCBGgptYXgAMwUALQYAgg2BFEFQUACCdCoAIgsAgxYFAIMPCyoiQVBQAIMOCF9hcHAoAIJvBiwAgXUPKQoKACUFLT4rACsHbWFpbl9sb29wAIU5B0FQUAAPBSAADgYAJQkAgwAPcGluZygAgnwOAIR8EQBZCHgAgy0GXwCGXAZfbmV4dAA7BQCBQIFRAIMQBgCCWwUAgXYKcXVpdAoKAIIwGmRvbmUAgycHAIIrGEdvb2QgYnllIQBUCgCGMA4gaXMgZmluaXNoZWQKCmRlc3Ryb3kgAIQPBQCHNQwAhmgOZG9uZSB3aXRoAIdABgCHaIFW&s=earth)

Current HB server prototype is `heartbeat.py`. It runs using Python 3: `python3 heartbeat.py`
It also supports for following queries:
 * `/list`: response will contain a list of APP_IDs for currently active applications
 * `/status`: general host status: there should be a single application
 * `/status?0&appid=APP_ID`: HB status of specified application. The response on status query can be directly sent to Nagios.
 
Samples:
 * [check_heartbeat.py](../server/check_heartbeat.py)
 * [function `check_hilbert_heartbeat` from `check_hilbert.sh`](https://github.com/hilbert/hilbert-docker-images/blob/devel/images/omd_agent/check_hilbert.sh)
 * [prototype client in Python3](../client/python/)
 * [helpers in BASH](../client/bash/)
