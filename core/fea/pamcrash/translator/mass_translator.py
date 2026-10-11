"""Write isotropic concentrated node masses using native PAM MASS cards."""
from core.fea.translator import Translator
from .selection import field


class MassTranslator(Translator):
    def translate(self, version):
        lines = []
        for mass in self.dataframe.storge.get('element_mass', {}).values():
            if mass.nid not in self.dataframe.node or mass.mass < 0:
                raise ValueError(f'PAM MASS: invalid node or mass for {mass.uid}')
            lines += [
                'MASS  / ' + field(mass.nid) + field(0) + ' ' * 8
                + ''.join(field(0.0, 16) for _ in range(3)) + '\n',
                f'NAME source_mass_{mass.uid}\n',
                ' ' * 8 + ''.join(field(float(mass.mass), 16) for _ in range(3)) + '\n',
                ' ' * 8 + ''.join(field(0.0, 16) for _ in range(3)) + '\n',
            ]
        self.dataframe.output_storge['MASS'] = lines
