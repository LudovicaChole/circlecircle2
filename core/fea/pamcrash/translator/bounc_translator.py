from core.fea.translator import Translator
from .selection import field


class BouncTranslator(Translator):
    def translate(self, version):
        lines = []
        for obj in self.dataframe.storge['boundary_spc_node'].values():
            mask = ''.join('1' if i in obj.dofs else '0' for i in range(1,7))
            lines += ['BOUNC / '+field(obj.uid)+'  '+mask+field(0)+field(0)+'\n',f'NAME constraint_{obj.uid}\n']
        self.dataframe.output_storge.setdefault('BOUNC', []).extend(lines)
