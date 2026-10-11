"""Use unique Abaqus labels while leaving material matching fingerprints intact."""
import re


def material_names(df):
    used = set()
    for mid, material in df.material.items():
        base = re.sub(r'[^A-Za-z0-9_]', '_', str(material.name)).strip('_') or f'mat_{mid}'
        if not base[0].isalpha():
            base = 'mat_' + base
        # Reserve room for the section prefix in combined property labels.
        base = base[:48]
        name, suffix = base, 0
        while name.upper() in used:
            suffix += 1
            name = f'{base}_{mid}_{suffix}'
        used.add(name.upper())
        material.name = name
    # Section names become ELSET labels in the flat Abaqus model. Dots are
    # reserved for assembly qualification and cannot appear in these labels.
    used = set()
    for sections in (df.section_shell, df.section_solid):
        for sid, section in sections.items():
            base = re.sub(r'[^A-Za-z0-9_]', '_', str(section.name)).strip('_') or f'section_{sid}'
            if not base[0].isalpha():
                base = 'section_' + base
            base = base[:24]
            name = base
            suffix = 0
            while name.upper() in used:
                suffix += 1
                name = f'{base}_{sid}_{suffix}'
            used.add(name.upper())
            section.name = name
