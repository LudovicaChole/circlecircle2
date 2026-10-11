"""Linear shell/solid connectivity in the common LS-DYNA node ordering."""
from core.fea.model.lsdyna.element_shell import ElementShell
from core.fea.model.lsdyna.element_solid import ElementSolid
from core.fea.mesh_data import insert


class ElementParser:
    counts = {'S3': 3, 'S3R': 3, 'S4': 4, 'S4R': 4, 'C3D4': 4,
              'C3D5': 5, 'C3D6': 6, 'C3D8': 8, 'C3D8R': 8, 'C3D8I': 8, 'MASS': 1}

    def parse(self, options, rows, df, sets):
        kind = options.get('TYPE', '').upper()
        if kind not in self.counts:
            raise ValueError(f'ELEMENT: unsupported type {kind}')
        if set(options) - {'TYPE', 'ELSET'}:
            raise ValueError('ELEMENT: unsupported parameters')
        pending = ''
        for line in rows:
            pending += line.strip()
            if line.rstrip().endswith(','):
                continue
            values = [int(v.strip()) for v in pending.split(',')]
            pending = ''
            eid, *nodes = values
            if len(nodes) != self.counts[kind] or min(values) <= 0:
                raise ValueError(f'ELEMENT {eid}: invalid {kind} connectivity')
            if eid in df.element_solid or eid in df.element_shell or eid in df.storge['element_mass']:
                raise ValueError(f'Duplicate element {eid}')
            if kind == 'MASS':
                from types import SimpleNamespace
                df.storge['element_mass'][eid] = SimpleNamespace(uid=eid,nid=nodes[0],mass=0,pid=0)
                if 'ELSET' in options:
                    sets.setdefault(options['ELSET'].upper(), []).append(eid)
                continue
            if kind.startswith('S'):
                nodes += [nodes[-1]]*(4-len(nodes))
                record = ElementShell(uid=eid, pid=0, **{f'n{i+1}': n for i,n in enumerate(nodes)})
                store = df.element_shell
            else:
                if len(nodes) == 6:
                    # Inverse of the established DYNA -> Abaqus wedge permutation.
                    a,b,c,d,e,f = nodes
                    nodes = [a,c,f,d,b,b,e,e]
                else:
                    nodes += [nodes[-1]]*(8-len(nodes))
                record = ElementSolid(uid=eid, pid=0, **{f'n{i+1}': n for i,n in enumerate(nodes)})
                store = df.element_solid
            insert(store, record)
            if 'ELSET' in options:
                sets.setdefault(options['ELSET'].upper(), []).append(eid)
        if pending:
            raise ValueError('ELEMENT: incomplete continuation')
