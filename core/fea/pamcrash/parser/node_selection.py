"""Resolve explicit PAM node selections, ranges, groups and removals."""
import shlex


def nodes(rows, df, active=()):
    result = set()
    for row in rows:
        tokens = shlex.split(row)
        if not tokens or tokens[0] in ('END', 'NAME', 'META'):
            continue
        kind, *values = tokens
        remove = kind.startswith('DEL')
        kind = kind[3:] if remove else kind
        selected = set()
        if kind in ('GRP', 'OGRP'):
            for name in values:
                if name in active:
                    raise ValueError(f'Cyclic GROUP reference {name}')
                group = df.storge['pam_groups'].get(name)
                if group is None:
                    raise ValueError(f'Undefined GROUP {name}')
                selected.update(nodes(group.rows, df, (*active, name)))
        elif kind in ('ELE', 'PART'):
            mesh = {**df.element_shell, **df.element_solid}
            available = set(mesh) if kind == 'ELE' else set(df.part)
            selected_ids = set()
            for token in values:
                if ':' in token:
                    first,last = map(int,token.split(':'))
                    if first <= 0 or last < first:
                        raise ValueError(f'Invalid {kind} range {token}')
                    selected_ids.update(n for n in available if first <= n <= last)
                else:
                    entity = int(token)
                    if entity not in available:
                        raise ValueError(f'Missing selected {kind} {entity}')
                    selected_ids.add(entity)
            elements = [mesh[eid] for eid in selected_ids] if kind == 'ELE' else [e for e in mesh.values() if e.pid in selected_ids]
            for element in elements:
                selected.update(getattr(element,f'n{i}') for i in range(1,9) if getattr(element,f'n{i}',0))
        elif kind == 'NOD':
            for token in values:
                if ':' in token:
                    ends = token.split(':')
                    if len(ends) != 2:
                        raise ValueError(f'Unsupported node range {token}')
                    first,last = map(int, ends)
                    if first <= 0 or last < first:
                        raise ValueError(f'Invalid node range {token}')
                    # PAM ranges select existing entities; absent labels are not invented.
                    selected.update(n for n in df.node if first <= n <= last)
                else:
                    nid = int(token)
                    if nid not in df.node:
                        raise ValueError(f'Missing selected node {nid}')
                    selected.add(nid)
        else:
            raise ValueError(f'Unsupported node-selection operator {kind}')
        if remove:
            result.difference_update(selected)
        else:
            result.update(selected)
    return sorted(result)
