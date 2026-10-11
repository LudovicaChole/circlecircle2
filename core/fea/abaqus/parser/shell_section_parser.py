from core.fea.model.lsdyna.section_shell import SectionShell


class ShellSectionParser:
    def parse(self, options, rows, sid):
        if set(options) - {'ELSET', 'MATERIAL', 'OFFSET', 'SECTION INTEGRATION'}:
            raise ValueError('SHELL SECTION: only homogeneous isotropic sections are supported')
        if float(options.get('OFFSET', 0)) != 0:
            raise ValueError('SHELL SECTION: nonzero OFFSET requires reference-surface conversion')
        if len(rows) != 1:
            raise ValueError('SHELL SECTION: expected one homogeneous thickness card')
        values = [v.strip() for v in rows[0].split(',')]
        h = float(values[0])
        rule = options.get('SECTION INTEGRATION', 'SIMPSON').upper()
        if rule not in ('SIMPSON', 'GAUSS'):
            raise ValueError(f'SHELL SECTION: unknown integration rule {rule}')
        nip = int(values[1]) if len(values)>1 and values[1] else (3 if rule == 'GAUSS' else 5)
        if h <= 0 or nip <= 0:
            raise ValueError('SHELL SECTION: thickness and integration count must be positive')
        return SectionShell(uid=sid, t1=h, t2=h, t3=h, t4=h, nip=nip, name=f'p_shell_{sid}')
