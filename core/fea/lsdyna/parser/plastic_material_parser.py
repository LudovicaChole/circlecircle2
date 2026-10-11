from core.fea.parser import Parser
from .card_fields import fields, number
from core.fea.model.lsdyna.mat_piecewise_linear_plasticity_log_interpolation import MatPiecewiseLinearPlasticityLogInterpolation
from core.fea.model.lsdyna.mat_modified_piecewise_linear_plasticity import MatModifiedPiecewiseLinearPlasticity
from core.fea.model.lsdyna.mat_barlat_yld2000 import MatBarlatYld2000


COMMON = ['uid rho e pr sigy etan fail tdel', 'c p lcss lcsr vp lcf',
          'eps1 eps2 eps3 eps4 eps5 eps6 eps7 eps8', 'es1 es2 es3 es4 es5 es6 es7 es8']
SCHEMAS = {
    'MAT_PIECEWISE_LINEAR_PLASTICITY_LOG_INTERPOLATION': (MatPiecewiseLinearPlasticityLogInterpolation, COMMON),
    'MAT_MODIFIED_PIECEWISE_LINEAR_PLASTICITY': (MatModifiedPiecewiseLinearPlasticity,
        [COMMON[0], 'c p lcss lcsr vp epsthin epsmaj numint', *COMMON[2:]]),
    'MAT_BARLAT_YLD2000': (MatBarlatYld2000, [
        'uid rho e pr fit beta iter iscale', 'k e0 n c p hard a',
        'alpha1 alpha2 alpha3 alpha4 alpha5 alpha6 alpha7 alpha8',
        'aopt offang p4 htflag hta htb htc htd', '_ _ _ a1 a2 a3',
        'v1 v2 v3 d1 d2 d3 usrfail']),
}


class PlasticMaterialParser(Parser):
    def __init__(self, keyword, title=False):
        super().__init__()
        self.keyword, self.title = keyword, title
        self.version = {'12.0': self._read, '13.0': self._read, "16.0": self._read}

    def _read(self, line_raw):
        index = self.line_number - int(self.title)
        self.line_number += 1
        if index == -1:
            self.temp.append(line_raw.strip())
            return
        cls, cards = SCHEMAS[self.keyword]
        if index >= len(cards):
            if line_raw.strip():
                raise ValueError(f'{self.keyword}: unexpected extra data card')
            return
        values = {name: number(raw, self.dataframe, integer=name in ('uid', 'lcss', 'lcsr', 'lcf', 'hard'))
                  for name, raw in zip(cards[index].split(), fields(line_raw)) if name != '_'}
        if index == 0:
            obj = cls(**values, **({'name': self.temp[0]} if self.title else {}))
            obj.keyword = self.keyword
            self.current_id = obj.uid
            self.dataframe.material[obj.uid] = obj
            self.dataframe.storge_material_id.append(obj.uid)
        else:
            obj = self.dataframe.material[self.current_id]
            for name, value in values.items():
                setattr(obj, name, value)
