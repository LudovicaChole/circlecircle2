from core.fea.parser import Parser
from core.fea.model.lsdyna.mat_add_erosion import MatAddErosion
from .card_fields import fields, number


class MatAddErosionParser(Parser):
    card_names = (
        'uid excl mxpres mneps effeps voleps numfip ncs',
        'mnpres sigp1 sigvm mxeps epssh sigth impulse failtm',
        'idam dmgtyp lcsdg ecrit dmgexp dcrit fadexp lcregd',
        'sizflg refsz nahsv lcsrs shrf biaxf',
        'lcfld nsff epsthin engcrt radcrt lceps12 lceps13 lcepsmx',
        'dteflt volfrac mxtmp dtmin',
    )
    integers = {'uid', 'idam', 'lcsdg', 'lcregd', 'lcfld', 'nsff', 'lceps12', 'lceps13', 'lcepsmx'}

    def __init__(self, title=False):
        super().__init__()
        self.title = title
        self.version = {v: self._12p0 for v in ('12.0', '13.0', '16.0')}

    def _12p0(self, line_raw):
        index = self.line_number - int(self.title)
        self.line_number += 1
        if index == -1:
            self.temp = [{'name': line_raw.strip()}]
            return
        card_index = index
        if index >= 3 and getattr(self.current_material, 'idam', 0) == 0:
            card_index += 1
        if card_index >= len(self.card_names):
            if line_raw.strip():
                raise ValueError('MAT_ADD_EROSION: unexpected extra data card')
            return
        values = {name: number(raw, self.dataframe, integer=name in self.integers)
                  for name, raw in zip(self.card_names[card_index].split(), fields(line_raw))}
        if index == 0:
            self.current_material = MatAddErosion(**values, **(self.temp[0] if self.title else {}))
            self.dataframe.mat_add_erosion[self.current_material.uid] = self.current_material
        else:
            for name, value in values.items():
                setattr(self.current_material, name, value)
