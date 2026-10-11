from core.fea.translator import Translator
from .card_fields import field


class NodeTranslator(Translator):
    def translate(self, version):
        lines = ['*NODE\n'] if self.dataframe.node else []
        lines += [field(n.uid,8)+''.join(field(v,16) for v in n.xyz)+'\n' for n in self.dataframe.node.values()]
        self.dataframe.output_storge['*NODE'] = lines
