"""Abaqus single-node MASS elements with independent properties and source ownership."""


def point_mass_cards(df):
    lines = []
    used = set(df.element_shell) | set(df.element_solid)
    masses = df.storge.get('element_mass', {})
    next_element = max(used | set(masses), default=0) + 1
    next_property = max(set(df.section_shell) | set(df.section_solid) |
                        set(df.section_beam) | set(df.material), default=0) + 1
    next_component = max(df.part, default=0) + 1
    labels = {p.name.upper() for p in df.part.values()}
    for mass in masses.values():
        if mass.nid not in df.node:
            raise ValueError(f'ELEMENT_MASS {mass.uid}: missing node {mass.nid}')
        eid = mass.uid
        if eid in used:
            eid, next_element = next_element, next_element + 1
        used.add(eid)
        label = f'point_mass_{mass.uid}'
        while label.upper() in labels:
            label += '_mass'
        labels.add(label.upper())
        owner = df.part.get(getattr(mass, 'pid', 0))
        if owner:
            component_id, component_name = owner.uid, owner.name
        else:
            component_id, component_name = next_component, label
            next_component += 1
        lines.extend([
            '** Point mass: one connected node; independent MASS property.\n',
            f'**HW_COMPONENT ID={component_id} COLOR=7 NAME={component_name}\n',
            f'*ELEMENT, TYPE=MASS, ELSET={label}\n', f'{eid}, {mass.nid}\n',
            f'**HMNAME PROPERTY {next_property:10d} {label}\n',
            f'*MASS, ELSET={label}\n', f'{mass.mass:.12g}\n'])
        next_property += 1
    return lines
