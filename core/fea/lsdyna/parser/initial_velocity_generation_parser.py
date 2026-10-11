from core.fea.parser import Parser
from core.fea.model.lsdyna.initial_velocity_generation import InitialVelocityGeneration
from .card_fields import fields, number


class InitialVelocityGenerationParser(Parser):
    def __init__(self, title=False):
        super().__init__()
        self.title = title
        self.version = {"12.0": self._read, "13.0": self._read, "16.0": self._read}

    def _read(self, line_raw):
        index = self.line_number - int(self.title)
        self.line_number += 1
        if index == -1:
            self.temp.append(line_raw.strip())
            return
        names = ('pid styp omega vx vy vz ivant lcid', 'xc yc zc nx ny nz phase irigid')
        if index > 1:
            raise ValueError('Unexpected INITIAL_VELOCITY_GENERATION card')
        values = {name: number(raw, self.dataframe, 0,
                              integer=name in ('pid','styp','ivant','lcid','phase','irigid'))
                  for name, raw in zip(names[index].split(), fields(line_raw))}
        if index == 0:
            self.current_id = len(self.dataframe.initial_velocity_generation) + 1
            self.obj = InitialVelocityGeneration(uid=self.current_id, **values,
                **({'name': self.temp[0]} if self.title else {}))
            self.dataframe.initial_velocity_generation[self.current_id] = self.obj
        else:
            for name, value in values.items():
                setattr(self.obj, name, value)
