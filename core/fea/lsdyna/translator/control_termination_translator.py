from core.fea.translator import Translator
from .card_fields import card


class ControlTerminationTranslator(Translator):
    def translate(self, version):
        lines = []
        for obj in self.dataframe.control_termination.values():
            lines += ['*CONTROL_TERMINATION\n', card((obj.endtim,))]
        self.dataframe.output_storge['*CONTROL_TERMINATION'] = lines
