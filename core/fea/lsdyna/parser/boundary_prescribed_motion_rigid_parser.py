from core.fea.parser import Parser
from core.fea.lsdyna.keywords.boundary_prescribed_motion_rigid import BoundaryPrescribedMotionRigid
from .card_fields import fields, number


class BoundaryPrescribedMotionRigidParser(Parser):
    def __init__(self):
        super().__init__()
        self.version = {"12.0": self._read, "13.0": self._read}

    def _read(self, line_raw):
        if not line_raw.strip():
            return
        names = 'typeid dof vad lcid sf vid death birth'.split()
        defaults = [0, 0, 0, 0, 1.0, 0, 1e28, 0.0]
        values = {name: number(raw, self.dataframe, defaults[i], integer=i in (0, 1, 2, 3, 5))
                  for i, (name, raw) in enumerate(zip(names, fields(line_raw)))}
        uid = len(self.dataframe.boundary_prescribed_motion_rigid) + 1
        obj = BoundaryPrescribedMotionRigid(uid=uid, **values)
        for name, value in values.items():
            setattr(obj, name, value)
        self.dataframe.boundary_prescribed_motion_rigid[uid] = obj
