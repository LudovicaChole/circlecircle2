from core.fea.parser import Parser
from core.fea.lsdyna.keywords.mat_piecewise_linear_plasticity_log_interpolation import MatPiecewiseLinearPlasticityLogInterpolation
from .card_fields import fields, number
from core.fea.lsdyna.material_mapper import material_mapper


class MatPiecewiseLinearPlasticityParser(Parser):
    def __init__(self, title=False):
        super().__init__()
        self.title = title
        self.version = {"12.0": self._read, "13.0": self._read}

    def _read(self, line_raw):
        index = self.line_number - int(self.title)
        self.line_number += 1
        if index == -1:
            self.temp.append(line_raw.strip())
            return
        cards = ["uid rho e pr sigy etan fail tdel", "c p lcss lcsr vp lcf", "eps1 eps2 eps3 eps4 eps5 eps6 eps7 eps8", "es1 es2 es3 es4 es5 es6 es7 es8"]
        if index >= len(cards):
            raise ValueError("Unexpected MAT24 data card")
        data = {name: number(raw, self.dataframe, 1e21 if name == 'fail' else 0, integer=name in ('uid', 'lcss', 'lcsr', 'lcf'))
                for name, raw in zip(cards[index].split(), fields(line_raw))}
        if index == 0:
            obj = MatPiecewiseLinearPlasticityLogInterpolation(**data, **({'name': self.temp[0]} if self.title else {}))
            obj.keyword = 'MAT_PIECEWISE_LINEAR_PLASTICITY'
            if not self.title:
                obj.name = f'mat_{obj.uid}'
            self.current_id = obj.uid
            self.dataframe.material[obj.uid] = obj
            self.dataframe.storge_material_id.append(obj.uid)
        else:
            obj = self.dataframe.material[self.current_id]
            for name, value in data.items():
                setattr(obj, name, value)
            if index == 1:
                obj.map_tag = material_mapper.map_material(lcss_id=obj.lcss)
