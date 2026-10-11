"""Resolve supported native general-contact domains and property assignments."""
from types import SimpleNamespace


def contact_pairs(content, df, surfaces, interactions, options):
    active, inclusions, assignments = False, [], []
    for location, header, rows in content:
        keyword, opts = options(header)
        if keyword == '*CONTACT':
            if active:
                raise ValueError('Multiple general contact domains or step changes are not mapped')
            if set(opts) - {'OP'} or opts.get('OP', 'NEW').upper() != 'NEW':
                raise ValueError('Only a new general contact domain is mapped')
            active = True
        elif keyword in ('*CONTACT INCLUSIONS', '*CONTACT PROPERTY ASSIGNMENT', '*CONTACT EXCLUSIONS'):
            if not active:
                raise ValueError(f'{keyword}: missing CONTACT domain')
            if keyword == '*CONTACT EXCLUSIONS':
                raise ValueError('General contact exclusions require explicit contact-domain mapping')
            if keyword == '*CONTACT INCLUSIONS':
                if set(opts) - {'ALL EXTERIOR'}:
                    raise ValueError('Unsupported contact inclusion options')
                if 'ALL EXTERIOR' in opts:
                    if rows:
                        raise ValueError('ALL EXTERIOR must not have data rows')
                    inclusions.append(('', '', location))
                else:
                    for row in rows:
                        values = [v.strip().upper() for v in row.split(',')]
                        if len(values) > 2:
                            raise ValueError('Invalid contact inclusion row')
                        inclusions.append((values[0], values[1] if len(values)>1 else '', location))
            else:
                if opts:
                    raise ValueError('Unsupported contact property assignment options')
                for row in rows:
                    values = [v.strip().upper() for v in row.split(',')]
                    if not 3 <= len(values) <= 5 or any(v not in ('', 'SURFACE') for v in values[3:]):
                        raise ValueError('Only surface-based contact property assignments are mapped')
                    if any(name and name not in surfaces for name in values[:2]):
                        raise ValueError('Contact property assignment references an undefined surface')
                    if values[2] not in interactions:
                        raise ValueError(f'Undefined surface interaction {values[2]}')
                    assignments.append(values[:3])
    if not active:
        return []
    if not inclusions:
        raise ValueError('General contact domain has no inclusions')
    result = []
    for first, second, location in inclusions:
        second = second or first
        property_name = None
        def facets(name):
            return {frozenset(face) for face in surfaces[name].facets} if name else set()
        for a, b, name in assignments:
            b = b or a
            if (not a and not b) or (a, b) in ((first, second), (second, first)):
                property_name = name
            elif not first and not second and (a or b):
                # Assignments on only part of an inclusion cannot be replaced
                # by a single uniform LS-DYNA friction coefficient.
                raise ValueError('Contact property assignment subdivides an inclusion; split the domain explicitly')
            elif a and b:
                domain = (facets(first), facets(second))
                assigned = (facets(a), facets(b))
                if assigned == domain or assigned[::-1] == domain:
                    property_name = name
                elif ((domain[0] & assigned[0] and domain[1] & assigned[1]) or
                      (domain[0] & assigned[1] and domain[1] & assigned[0])):
                    raise ValueError('Contact property assignment subdivides an inclusion; split the domain explicitly')
        coefficient = interactions[property_name] if property_name else 0.0
        if first:
            slave = surfaces[first]
            master = surfaces[second]
        elif second:
            raise ValueError('Pairing a named surface with ALL EXTERIOR is not mapped')
        else:
            slave = master = SimpleNamespace(sid=0, selection_type=5, nodes=sorted(df.node), facets=[])
        result.append((slave, master, coefficient, location))
    return result
