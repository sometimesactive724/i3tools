#!/usr/bin/env python3
from i3_ipc import I3Ipc
import json
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
    root = wm_con.request(wm_con.TREE, b'', 'json')
    assert root['type'] == 'root'
    workspaces = {}
    focused = None
    for output in root['nodes']:
        assert output['type'] == 'output'
        for workspace in output['nodes']:
            assert workspace['type'] == 'workspace'
            for client in workspace['nodes']:
                assert client['type'] == 'con' and not client['nodes']
                name = int(workspace['name'])
                if client['focused']:
                    focused = name
                workspaces.setdefault(name, []).append(client['id'])
    keys = sorted(workspaces)
    wm_con.request(wm_con.SUBSCRIBE, b'["window"]')
    if focused is None:
        assert not keys
    for i in () if focused is None else iterate_in_an_order(keys.index(focused), keys):
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
