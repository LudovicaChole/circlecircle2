from core.fea.translator import Translator
from .card_fields import card


class ElementShellTranslator(Translator):
    def translate(self, version):
        lines = ['*ELEMENT_SHELL\n'] if self.dataframe.element_shell else []
        lines += [card((e.uid,e.pid,e.n1,e.n2,e.n3,e.n4),8) for e in self.dataframe.element_shell.values()]
        self.dataframe.output_storge['*ELEMENT_SHELL'] = lines
