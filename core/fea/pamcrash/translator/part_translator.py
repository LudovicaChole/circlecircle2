from core.fea.translator import Translator
from .selection import field


class PartTranslator(Translator):
    def __init__(self):
        super().__init__()
        self.version = {'2020': self._write, '2023': self._write}

    def translate(self, version):
        self._write()

    def _write(self):
        df, lines = self.dataframe, []
        from .hourglass_translator import HourglassTranslator
        controls = HourglassTranslator().translate(None)
        shell_materials = {p.mid for p in df.part.values() if p.secid in df.section_shell}
        solid_ids = {}
        next_id = max(df.material, default=0)
        for pid, part in df.part.items():
            mid = part.mid
            if mid not in df.material:
                raise ValueError(f'Part {pid}: missing material {mid}')
            if part.secid in df.section_shell:
                kind, thickness = 'SHELL', field(df.section_shell[part.secid].t1, 10)
            elif part.secid in df.section_solid:
                kind, thickness = 'SOLID', ' '*10
                if mid not in solid_ids:
                    if mid in shell_materials:
                        next_id += 1
                        solid_ids[mid] = next_id
                    else:
                        solid_ids[mid] = mid
                    df.storge_pam_elastic_solid_material[solid_ids[mid]] = df.material[mid]
                mid = solid_ids[mid]
            else:
                raise ValueError(f'Part {pid}: unsupported section {part.secid}')
            lines.extend(['PART  / ' + field(pid) + field(kind) + field(mid) +
                          field(0)*3 + field(controls.get(pid, 0)) + '\n',
                          f'NAME {part.name}\n', '       0.0       1.0\n', ' '*30+'\n',
                          thickness+' '*20+'\n', ' '*30+'\n', 'END_PART\n'])
        df.output_storge['PART'] = lines
