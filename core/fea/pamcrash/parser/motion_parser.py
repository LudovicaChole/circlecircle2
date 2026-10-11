"""Global PAM *3D prescribed motion; columns follow Altair loads_2016."""
from types import SimpleNamespace
from core.fea.parser import Parser
from .card_fields import value
from .node_selection import nodes
from core.fea.model.lsdyna.define_curve import DefineCurve


class MotionParser(Parser):
    def __init__(self, vad, rotational=False):
        super().__init__()
        self.vad, self.rotational = vad, rotational
        self.version = {v: lambda line: self.temp.append(line.rstrip()) for v in ('2020', '2023')}

    def finish(self):
        if not self.temp:
            return
        h = self.temp[0]
        nid = value(h[8:16], integer=True)
        if nid and nid not in self.dataframe.node:
            raise ValueError(f'Prescribed motion: missing node {nid}')
        if value(h[64:72], integer=True) or value(h[72:80], integer=True):
            raise ValueError('Prescribed motion: local frames and sensors are not mapped')
        rows = list(self.temp[1:])
        constants = [0.0]*3
        if h[80:81] == '&':
            if not rows or rows[0].startswith('NAME'):
                raise ValueError('Prescribed motion: missing constant continuation card')
            card = rows.pop(0)
            constants = [value(card[8+16*i:24+16*i]) for i in range(3)]
            if card[80:81] == '&':
                raise ValueError('Prescribed motion: imaginary harmonic constants are not mapped')
        rows = [r for r in rows if r.strip() and not r.startswith('NAME')]
        selected = nodes(rows, self.dataframe) if not nid else [nid]
        if nid and rows:
            raise ValueError('Prescribed motion: node-selection cards require IDNOD=0')
        if not selected:
            raise ValueError('Prescribed motion: empty node selection')
        store = self.dataframe.storge['prescribed_motion_node']
        pending = []
        for axis in range(3):
            cid = value(h[16+axis*8:24+axis*8], integer=True)
            if not cid:
                if not constants[axis]:
                    continue  # Zero constants leave this DOF free (ACC3D manual).
                cid = max(set(self.dataframe.define_curve) | set(self.dataframe.define_table), default=0)+1
                curve = DefineCurve(uid=cid, name=f'pam_constant_motion_{cid}')
                curve.a1, curve.o1 = [0.0, 1.0], [constants[axis]]*2
                self.dataframe.define_curve[cid] = curve
                sf = 1.0
            else:
                if constants[axis]:
                    raise ValueError('Prescribed motion: simultaneous function and constant require explicit conversion')
                sf = value(h[40+axis*8:48+axis*8], default=1)
            if cid not in self.dataframe.define_curve:
                raise ValueError(f'Prescribed motion: undefined FUNCT {cid}')
            dof = axis+1+(3 if self.rotational else 0)
            for node in selected:
                if any(m.nid == node and m.dof == dof for m in store.values()):
                    raise ValueError(f'Duplicate prescribed motion at node {node}, DOF {dof}')
                pending.append(dict(nid=node, dof=dof, vad=self.vad, lcid=cid, sf=sf, birth=0, death=1e28))
        for attributes in pending:
            uid = max(store, default=0)+1
            store[uid] = SimpleNamespace(uid=uid, **attributes)
        self.reset()
