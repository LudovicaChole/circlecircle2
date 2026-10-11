from core.fea.translator import Translator
from .card_fields import card
from .section_shell_translator import thickness_name
import re


class PartTranslator(Translator):
    def translate(self, version):
        lines = []
        names = set()
        for p in self.dataframe.part.values():
            if self.dataframe.solver == 'abaqus' and p.secid in self.dataframe.section_shell:
                section = self.dataframe.section_shell[p.secid]
                # Keep the material suffix of generated Abaqus ELSET names.
                match = re.fullmatch(r'p_shell_\d+(?:_\d+)?_(.+)', p.name)
                material = match.group(1) if match else self.dataframe.material[p.mid].name
                name = f'{thickness_name(section.t1)}_{material}'
                p.name = name if name not in names else f'{name}_part{p.uid}'
            names.add(p.name)
            lines += ['*PART\n', p.name+'\n', card((p.uid,p.secid,p.mid,p.eosid,p.hgid))]
        self.dataframe.output_storge['*PART'] = lines
