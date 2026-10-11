from core.fea.translator import Translator
from .selection import field
from core.fea.abaqus.translator.analysis_data import velocity_field


class InvelTranslator(Translator):
    def translate(self, version):
        lines = []
        for nid,components in sorted(velocity_field(self.dataframe).items()):
            lines += ['INVEL / '+''.join(field(v) for v in (nid,*components,0,0))+'\n',f'NAME velocity_{nid}\n']
        self.dataframe.output_storge['INVEL'] = lines
