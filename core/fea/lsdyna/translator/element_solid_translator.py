from core.fea.translator import Translator
from .card_fields import card


class ElementSolidTranslator(Translator):
    def translate(self, version):
        lines = ['*ELEMENT_SOLID\n'] if self.dataframe.element_solid else []
        for e in self.dataframe.element_solid.values():
            lines += [card((e.uid,e.pid),8), card([getattr(e,f'n{i}') for i in range(1,9)],8)]
        self.dataframe.output_storge['*ELEMENT_SOLID'] = lines
