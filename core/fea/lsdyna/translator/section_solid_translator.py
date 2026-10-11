from core.fea.translator import Translator
from .card_fields import card


class SectionSolidTranslator(Translator):
    def translate(self, version):
        lines = []
        for s in self.dataframe.section_solid.values():
            lines += ['*SECTION_SOLID\n', card((s.uid,s.elform))]
        self.dataframe.output_storge['*SECTION_SOLID'] = lines
