from types import SimpleNamespace
from core.fea.parser import Parser
from .card_fields import fields, number


class BoundaryPrescribedMotionNodeParser(Parser):
    def __init__(self):
        super().__init__()
        self.version = {v: self._read for v in ('12.0','13.0','16.0')}

    def _read(self, line):
        names = 'nid dof vad lcid sf vid death birth'.split()
        defaults = [0,0,0,0,1,0,1e28,0]
        values = {name: number(raw,self.dataframe,defaults[i],integer=i in (0,1,2,3,5))
                  for i,(name,raw) in enumerate(zip(names,fields(line)))}
        mapping = {1:1,2:2,3:3,5:4,6:5,7:6}
        if values['vid'] or values['dof'] not in mapping or values['vad'] not in (0,1,2):
            raise ValueError('Prescribed node motion: vector/local axes are not mapped')
        values['dof'] = mapping[values['dof']]
        store = self.dataframe.storge['prescribed_motion_node']
        uid = len(store)+1
        store[uid] = SimpleNamespace(uid=uid, **values)
