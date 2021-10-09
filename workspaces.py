#!/usr/bin/env python3
import sys
from i3_ipc import I3Ipc, Workspaces
def get(direction):
    (a, b) = {
        'next': ('max',  1),
        'prev': ('min', -1)
    }[direction]
    i = c.workspaces().info()
    return str(i.get(direction, i[a] + b)).encode('ascii')
def switch(direction, c):
    c.request(c.COMMAND, b'workspace ' + get(direction))
def move(direction, c):
    a = get(direction)
    c.request(c.COMMAND, b'move window workspace ' + a + b';workspace ' + a)
action = {
    'switch': switch,
    'move': move
}[sys.argv[1]]
with I3Ipc() as c:
    action(sys.argv[2], c)
