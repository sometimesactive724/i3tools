#!/usr/bin/env python3
import sys
from i3_ipc import I3Ipc
assert len(sys.argv) == 2 and sys.argv[1] in {'next', 'prev'}, "Usage: workspaces.py next|prev"
with I3Ipc() as i:
    w = i.workspace_info()
    (a, b) = {'next': ('max', 1), 'prev': ('min', -1)}[sys.argv[1]]
    i.request(i.COMMAND, b'workspace ' + str(w.get(sys.argv[1], w[a] + b)).encode('ascii'))
