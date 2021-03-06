#!/usr/bin/env python3
import json
from i3_ipc import I3Ipc
def iterate_in_an_order(start, collection):
    yield collection[start]
    a = start
    b = start
    c = True
    while c:
        a += 1
        b -= 1
        c = False
        if a < len(collection):
            yield collection[a]
            c = True
        if b >= 0:
            yield collection[b]
            c = True
with I3Ipc() as wm_con:
    tree = wm_con.tree()
    workspaces = tree.workspaces
    keys = sorted(workspaces)
    wm_con.request(wm_con.SUBSCRIBE, b'["window"]')
    for i in () if (focused := tree.focused) is None else iterate_in_an_order(keys.index(int(focused[1]['name'])), keys):
        wm_con.request(wm_con.COMMAND, b'workspace ' + str(i).encode('ascii'))
        for i in workspaces[i]:
            wm_con.request(wm_con.COMMAND, b'[con_id=' + str(i).encode('ascii') + b']kill')
            while True:
                (id, data) = wm_con.event()
                if id != 3:
                    continue
                data = json.loads(data)
                if data['change'] != 'close':
                    continue
                if data['container']['id'] == i:
                    break
