from core.fea.translator import Translator
from .card_fields import card
from core.fea.abaqus.translator.analysis_data import velocity_field


class InitialVelocityNodeTranslator(Translator):
    def translate(self, version):
        values = velocity_field(self.dataframe)
        lines = ['*INITIAL_VELOCITY_NODE\n'] if values else []
        lines += [card((nid,*components,0)) for nid,components in sorted(values.items())]
        self.dataframe.output_storge['*INITIAL_VELOCITY_NODE'] = lines
