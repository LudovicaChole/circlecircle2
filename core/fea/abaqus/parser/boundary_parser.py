from core.fea.model.lsdyna.boundary_spc_node import BoundarySpcNode
from .elset_parser import resolve


class BoundaryParser:
    def parse(self, options, rows, df, sets):
        if options:
            raise ValueError('BOUNDARY: only fixed model-data constraints are supported')
        aliases = {'ENCASTRE':(1,2,3,4,5,6), 'PINNED':(1,2,3),
                   'XSYMM':(1,5,6), 'YSYMM':(2,4,6), 'ZSYMM':(3,4,5),
                   'XASYMM':(2,3,4), 'YASYMM':(1,3,5), 'ZASYMM':(1,2,6)}
        store = df.storge['boundary_spc_node']
        for row in rows:
            fields = [v.strip().upper() for v in row.split(',')]
            selected = [int(fields[0])] if fields[0].isdecimal() else resolve(sets,fields[0])
            if fields[1] in aliases:
                if len(fields)>2 and any(fields[2:]):
                    raise ValueError('BOUNDARY: unexpected type-format values')
                dofs = aliases[fields[1]]
            else:
                first = int(fields[1])
                last = int(fields[2]) if len(fields)>2 and fields[2] else first
                if not 1 <= first <= last <= 6 or (len(fields)>3 and any(float(v) for v in fields[3:] if v)):
                    raise ValueError('BOUNDARY: only zero displacement/rotation constraints are supported')
                dofs = range(first,last+1)
            for nid in selected:
                if nid not in df.node:
                    raise ValueError(f'BOUNDARY: missing node {nid}')
                previous = store[nid].dofs if nid in store else ()
                store[nid] = BoundarySpcNode(nid,tuple(sorted(set(previous)|set(dofs))))
