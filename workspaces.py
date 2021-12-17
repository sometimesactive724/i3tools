#!/usr/bin/env python3
import sys
from i3_ipc import I3Ipc, Workspaces
def get(direction, c):
    w = c.workspaces()
    (a, b) = {
        'next': (w.next, w.max+1),
        'prev': (w.prev, w.min-1)
    }[direction]
    return str(b if a is None else a).encode('ascii')
def switch(direction, c):
    c.request(c.COMMAND, b'workspace ' + get(direction, c))
def move(direction, c):
    a = get(direction, c)
    c.request(c.COMMAND, b'move window workspace ' + a + b';workspace ' + a)
action = {
    'switch': switch,
    'move': move
}[sys.argv[1]]
with I3Ipc() as c:
    action(sys.argv[2], c)
