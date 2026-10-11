"""Extract material fragments from standalone solver decks.

Deck wrappers and unrelated model/control cards must never be embedded in a
material output block. HyperMesh metadata contains old entity IDs and is also
removed; native solver definitions remain authoritative after remapping.
"""


def material_fragment(text, solver):
    lines, active = [], False
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith(('$HM', '$HWCOLOR', '**HM')):
            continue
        if solver == 'lsdyna':
            if stripped.startswith('*'):
                keyword = stripped.split(',')[0].strip().upper()
                active = keyword.startswith(('*MAT_', '*DEFINE_CURVE', '*DEFINE_TABLE'))
        elif solver == 'pamcrash':
            from core.fea.include_reader import pam_keyword
            keyword = pam_keyword(line)
            if keyword:
                active = line[:8].strip() in ('MATER /', 'FUNCT /')
        elif solver == 'abaqus':
            if stripped.startswith('*') and not stripped.startswith('**'):
                keyword = stripped.split(',')[0].strip().upper()
                active = keyword.startswith((
                    '*MATERIAL', '*DENSITY', '*ELASTIC', '*PLASTIC', '*DAMAGE',
                    '*DEPVAR', '*USER MATERIAL', '*EXPANSION', '*DAMPING',
                    '*SPECIFIC HEAT', '*CONDUCTIVITY', '*RATE DEPENDENT',
                    '*VISCO', '*HYPERELASTIC', '*FAIL', '*EOS', '*CREEP',
                    '*POROUS', '*CAP ', '*DRUCKER', '*MOHR', '*CONCRETE',
                    '*SHEAR', '*TENSILE', '*TRS', '*LATENT HEAT'))
        else:
            raise ValueError(f'Unknown material template solver: {solver}')
        if active:
            lines.append(line)
    return '\n'.join(lines).rstrip() + '\n'
