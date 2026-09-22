from types import SimpleNamespace
from core.fea.parser import Parser
from .card_fields import fields, number


class MatAddDamageGissmoTitleParser(Parser):
    def __init__(self, title=True):
        super().__init__()
        self.title = title
        self.version = {"12.0": self._read, "13.0": self._read}

    def _read(self, line_raw):
        index = self.line_number - int(self.title)
        self.line_number += 1
        if index == -1:
            self.temp.append(line_raw.strip())
            return
        cards = ['mid unused dtyp refsz numfip', 'lcsdg ecrit dmgexp dcrit fadexp lcregd', 'lcsrs shrf biaxf lcdlim midfail hisvn soft lp2bi']
        if index >= len(cards):
            self.obj.extra_cards.append(line_raw.rstrip())
            return
        defaults = {'numfip': 1.0, 'dmgexp': 1.0, 'fadexp': 1.0}
        values = {name: number(raw, self.dataframe, defaults.get(name,0), integer=name == 'mid') for name, raw in zip(cards[index].split(), fields(line_raw))}
        if index == 0:
            self.obj = SimpleNamespace(name=self.temp[0] if self.title else '', extra_cards=[], **values)
            self.dataframe.storge.setdefault('mat_add_damage_gissmo', {})[self.obj.mid] = self.obj
        else:
            for name, value in values.items():
                setattr(self.obj, name, value)
