import math
from core.fea.model.lsdyna.initial_velocity_node import InitialVelocityNode
from .elset_parser import resolve


class InitialConditionsParser:
    def parse(self, options, rows, df, sets):
        if set(options) != {'TYPE'} or options['TYPE'].upper() != 'VELOCITY':
            raise ValueError('INITIAL CONDITIONS: only direct nodal velocities are supported')
        store = df.storge['initial_velocity_node']
        for row in rows:
            target,dof,raw = [v.strip().upper() for v in row.split(',')]
            selected = [int(target)] if target.isdecimal() else resolve(sets,target)
            dof, value = int(dof),float(raw)
            if not 1 <= dof <= 6 or not math.isfinite(value):
                raise ValueError('INITIAL CONDITIONS: invalid velocity component')
            for nid in selected:
                if nid not in df.node:
                    raise ValueError(f'INITIAL CONDITIONS: missing node {nid}')
                components = list(store[nid].components) if nid in store else [0.0]*6
                components[dof-1] = value
                store[nid] = InitialVelocityNode(nid,tuple(components))
