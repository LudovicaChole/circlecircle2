"""Write explicit part hourglass references and compatible Abaqus defaults."""
from core.fea.translator import Translator
from core.fea.model.lsdyna.hourglass import Hourglass
from core.fea.hourglass_controls import deformable_parts
from .card_fields import card


class HourglassTranslator(Translator):
    def translate(self, version):
        df = self.dataframe
        if df.solver == 'abaqus':
            profiles = {(h.ihq, h.qm): h.uid for h in df.hourglass.values()}
            for part in deformable_parts(df):
                if part.hgid or getattr(part, 'hourglass_from_global', False):
                    continue
                shell = df.section_shell.get(part.secid)
                profile = (8, .1) if shell and abs(shell.elform) == 16 else ((4, .05) if shell else (6, .1))
                if profile not in profiles:
                    uid = max(df.hourglass, default=0) + 1
                    df.hourglass[uid] = Hourglass(uid=uid, ihq=profile[0], qm=profile[1],
                                                q1=1.5, q2=.06, qb=None, qw=profile[1])
                    profiles[profile] = uid
                part.hgid = profiles[profile]
        for part in df.part.values():
            if part.hgid and part.hgid not in df.hourglass:
                raise ValueError(f'Part {part.uid}: missing hourglass {part.hgid}')
        df.output_storge['*HOURGLASS'] = [line for h in df.hourglass.values()
            for line in ('*HOURGLASS\n', card((h.uid, h.ihq, h.qm, h.ibq, h.q1, h.q2,
                                             " "*10 if h.qb is None else h.qb, h.qw)))]

        df.output_storge['*CONTROL_HOURGLASS'] = [line for h in df.control_hourglass.values()
            for line in ('*CONTROL_HOURGLASS\n', card((int(h.ihq), h.qh)))]
