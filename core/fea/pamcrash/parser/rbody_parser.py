"""Non-failing global RBODY types 0/1/2, following the local manual."""
from core.fea.parser import Parser
from core.fea.model.lsdyna.constrained_nodal_rigid_body import ConstrainedNodalRigidBody
from core.fea.model.lsdyna.set_node_list import SetNodeList
from .card_fields import value
from .node_selection import nodes


class RbodyParser(Parser):
    def __init__(self):
        super().__init__()
        self.version = {'2020': lambda line: self.temp.append(line.rstrip())}

    def finish(self):
        if not self.temp:
            return
        h = self.temp[0]
        uid, kind, ref = (value(h[a:b], integer=True) for a,b in ((8,16),(24,32),(32,40)))
        if kind not in (0,1,2) or value(h[56:64], integer=True):
            raise ValueError('RBODY: user mass/inertia types and sensors require explicit conversion')
        start = 2
        if kind in (1,2):
            failure = self.temp[2]
            if any(value(failure[i:i+8]) for i in range(8,80,8)):
                raise ValueError('RBODY: failing spotweld/rivet behavior cannot be replaced with a permanent coupling')
            start = 3
        selected = nodes(self.temp[start:], self.dataframe)
        if not selected or ref not in self.dataframe.node:
            raise ValueError(f'RBODY {uid}: empty node selection or missing reference {ref}')
        sid = max(self.dataframe.set_node_list, default=0)+1
        group = SetNodeList(uid=sid, name=f'pam_rbody_{uid}')
        group.ids = selected
        self.dataframe.set_node_list[sid] = group
        if uid in self.dataframe.constrained_nodal_rigid_body:
            raise ValueError(f'Duplicate RBODY {uid}')
        self.dataframe.constrained_nodal_rigid_body[uid] = ConstrainedNodalRigidBody(
            uid=uid, pid=uid, sid=sid, pnode=ref, name=self.temp[1][5:].strip())
        self.reset()
