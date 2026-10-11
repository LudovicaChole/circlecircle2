"""LS-DYNA revolute joint pairs and flexion-torsion property cards."""
from types import SimpleNamespace
from core.fea.parser import Parser
from .card_fields import fields, number


class RevoluteJointParser(Parser):
    def __init__(self, with_id=True):
        super().__init__()
        self.with_id = with_id
        self.version = {v:self.read for v in ('12.0','13.0','16.0')}
        self.cards = 2 if with_id else 1

    def read(self, line):
        if not line.strip():
            return
        if self.with_id and not self.temp:
            self.temp.append(line)
            return
        uid = number(fields(self.temp[0])[0], self.dataframe, integer=True) if self.with_id else max(self.dataframe.storge['joints'],default=0)+1
        values = [number(v,self.dataframe,integer=True) for v in fields(line)[:6]]
        if uid in self.dataframe.storge['joints'] or uid <= 0 or any(v<=0 for v in values[:4]):
            raise ValueError('REVOLUTE joint: invalid or duplicate joint/node identifiers')
        self.dataframe.storge['joints'][uid] = SimpleNamespace(uid=uid, nodes=tuple(values[:4]),
            rps=number(fields(line)[6],self.dataframe,default=1), damp=number(fields(line)[7],self.dataframe,default=1))
        self.temp.clear()


class JointStiffnessParser(Parser):
    def __init__(self):
        super().__init__()
        self.cards = 4
        self.version = {v:self.read for v in ('12.0','13.0','16.0')}

    def read(self, line):
        self.temp.append(line)
        if len(self.temp)<4:
            return
        rows = [tuple(number(v,self.dataframe) for v in fields(r)) for r in self.temp]
        uid = int(rows[0][0])
        if uid<=0 or uid in self.dataframe.storge['joint_stiffness']:
            raise ValueError('Joint stiffness: invalid or duplicate JSID')
        self.dataframe.storge['joint_stiffness'][uid] = SimpleNamespace(uid=uid,jid=int(rows[0][5]),rows=rows)
        self.temp.clear()
