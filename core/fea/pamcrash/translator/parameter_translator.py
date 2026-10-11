"""Preserve numeric parameter definitions as native PAM PYVAR blocks."""
import keyword
import math
from core.fea.translator import Translator
from .selection import field


class ParameterTranslator(Translator):
    def translate(self, version):
        lines = []
        for uid, parameter in enumerate(self.dataframe.parameter.values(), 1):
            name, value = parameter.name, parameter.value
            if not name.isidentifier() or keyword.iskeyword(name):
                raise ValueError(f'PAM PYVAR: invalid Python parameter name {name}')
            kind = getattr(parameter, 'type', 'R')
            if kind not in ('R', 'I') or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(f'PAM PYVAR: only finite numeric parameters are supported ({name})')
            literal = str(int(value)) if kind == 'I' else repr(float(value))
            lines += ['PYVAR / ' + field(uid) + '\n', f'NAME {name}\n',
                      f'{name} = {literal}\n', 'END_PYVAR\n']
        self.dataframe.output_storge['PYVAR'] = lines
