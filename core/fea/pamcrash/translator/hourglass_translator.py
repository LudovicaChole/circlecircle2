"""Component NUMPAR hourglass controls, independent of material templates."""
from core.fea.translator import Translator
from core.fea.hourglass_controls import deformable_parts
from .selection import field


class HourglassTranslator(Translator):
    def translate(self, version):
        df = self.dataframe
        self.part_controls = {}
        lines, profiles = [], {}
        notes = df.storge['hourglass_notes']
        definitions = {c['uid']: c['numpar'] for pid, c in notes.items()
                       if isinstance(pid, int) and c.get('numpar')}
        next_id = max(definitions, default=0)
        if df.solver == 'abaqus':
            lines.extend(definitions.values())
            for part in deformable_parts(df):
                restored = notes.get(part.uid)
                if restored is not None and (restored['uid'] or restored.get('ishg')):
                    self.part_controls[part.uid] = restored['uid']
                    continue
                kind = 'SHELL_LINEAR' if part.secid in df.section_shell else 'SOLID_LINEAR'
                if kind not in profiles:
                    next_id += 1
                    uid = next_id
                    profiles[kind] = uid
                    # ISHG=1 explicitly selects PAM's viscous control. Coefficients
                    # retain native defaults; no material/library fields are changed.
                    lines.extend(['NUMPAR/ ' + field(uid) + '\n',
                                  'NAME hourglass_' + kind.lower() + '\n', 'NUMBLOCK\n',
                                  ' ANALYSIS_TYPE                      EXPLICIT_MECHA\n',
                                  ' ELEMENT_TYPE                       ' + kind + '\n',
                                  ' HOURGLASS_FORMULATION               1\n',
                                  'END_NUMBLOCK\n', 'END_NUMPAR\n'])
                self.part_controls[part.uid] = profiles[kind]
        df.output_storge['NUMPAR'] = lines
        return self.part_controls
