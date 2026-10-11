from core.fea.translator import Translator
from .card_fields import card
from decimal import Decimal


def thickness_name(value):
    thickness = format(Decimal(format(value, '.12g')), 'f')
    if '.' in thickness:
        thickness = thickness.rstrip('0').rstrip('.')
    if '.' not in thickness:
        thickness += '.0'
    return thickness.replace('.', 'p') + 'mm'


def prepare_sections(df):
    """Name Abaqus shell sections by thickness and share identical cards."""
    if df.solver != 'abaqus':
        return
    unique, remap, names = {}, {}, set()
    for sid, section in list(df.section_shell.items()):
        key = tuple(getattr(section, field) for field in
                    ('elform', 'shrf', 'nip', 't1', 't2', 't3', 't4'))
        if key in unique:
            remap[sid] = unique[key]
            del df.section_shell[sid]
            continue
        unique[key] = sid
        name = thickness_name(section.t1)
        # Equal thickness with different integration/formulation must stay separate.
        section.name = name if name not in names else f'{name}_sec{sid}'
        names.add(name)
    for part in df.part.values():
        if part.secid in remap:
            part.secid = remap[part.secid]


class SectionShellTranslator(Translator):
    def translate(self, version):
        prepare_sections(self.dataframe)
        lines = []
        for s in self.dataframe.section_shell.values():
            if self.dataframe.solver == 'abaqus':
                lines += ['*SECTION_SHELL_TITLE\n', s.name + '\n']
            else:
                lines.append('*SECTION_SHELL\n')
            lines += [card((s.uid,s.elform,s.shrf,s.nip)), card((s.t1,s.t2,s.t3,s.t4))]
        self.dataframe.output_storge['*SECTION_SHELL'] = lines
