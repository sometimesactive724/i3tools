import sys
import os
import json
import math
import socket
from collections import deque
def _is_tree(root):
    if root['type'] != 'root': return False
    for output in root['nodes']:
        if output['type'] != 'output': return False
        for workspace in output['nodes']:
            if workspace['type'] != 'workspace': return False
            for client in workspace['nodes']:
                if client['type'] != 'con' or client['nodes']: return False
    return True
class I3IpcRaw(socket.socket):
    COMMAND = 0
    WORKSPACES = 1
    SUBSCRIBE = 2
    TREE = 4
    def __init__(self, sockpath = None, flags = socket.SOCK_STREAM):
        super().__init__(socket.AF_UNIX, socket.SOCK_STREAM)
        self.connect(os.environ['I3SOCK'] if sockpath is None else sockpath)
        self.queue = deque()
    def request(self, id, payload = b''):
        self.send(b'i3-ipc' + len(payload).to_bytes(4, sys.byteorder)+id.to_bytes(4, sys.byteorder)+payload)
    def process(self):
        data = self.recv(14)
        id = int.from_bytes(data[10:14], sys.byteorder)
        length = int.from_bytes(data[6:10], sys.byteorder)
        payload = self.recv(length)
        if id & 1<<31:
            self.queue.append((id & ~(1<<31), payload))
        return (id, payload)
class Tree:
    def __init__(self, root):
        assert _is_tree(root)
        self.root = root
    def focused(self):
        return next((
            (client, workspace, output)
            for output in self.root['nodes']
            for workspace in output['nodes']
            for client in workspace['nodes']
            if client['focused']
        ), None)
class Workspaces(tuple):
    def __new__(cls, workspaces):
        return super().__new__(cls, (next(int(i['name']) for i in workspaces if i['focused']), tuple(int(i['name']) for i in workspaces)))
    def info(self):
        focused = self[0]
        dist_next = math.inf
        dist_prev = math.inf
        min = math.inf
        max = -math.inf
        n = None
        p = None
        for position in self[1]:
            if max < position:
                max = position
            if min > position:
                min = position
            if focused < position and position - focused < dist_next:
                dist_next = position - focused
                n = position
            if focused > position and focused - position < dist_prev:
                dist_prev = focused - position
                p = position
        d = {
          'max': max,
          'min': min,
          'focused': focused,
        }
        if n is not None:
            d['next'] = n
        if p is not None:
            d['prev'] = p
        return d
class I3Ipc(I3IpcRaw):
    def request(self, id, payload = b'', *, output = None):
        super().request(id, payload)
        while (data := self.process())[0] != id:
            pass
        if output is None:
            return data[1]
        if output == 'json':
            return json.loads(data[1])
    def event(self):
        if self.queue:
            return self.queue.pop()
        else:
            data = self.process()
            return data[0] & ~(1<<31), data[1]
    def tree(self):
        return Tree(self.request(self.TREE, output='json'))
    def workspaces(self):
        return Workspaces(self.request(self.WORKSPACES, output='json'))
