"""Restore source motion notes, or read direct global Abaqus boundary loading."""
import math
from types import SimpleNamespace
from core.fea.model.lsdyna.define_curve import DefineCurve
from .elset_parser import resolve


def add_motion(df, nid, dof, vad, sf, points, birth=0.0, death=1e28):
    if not isinstance(nid,int) or nid <= 0 or dof not in range(1,7) or vad not in (0,1,2):
        raise ValueError('Invalid motion node/DOF/type')
    if not all(math.isfinite(v) for v in (sf,birth,death)) or not points:
        raise ValueError('Invalid motion scale/time/curve')
    if any(len(point)!=2 or not all(math.isfinite(v) for v in point) for point in points):
        raise ValueError('Invalid motion points')
    if any(b[0]<=a[0] for a,b in zip(points,points[1:])):
        raise ValueError('Motion time points must increase')
    store = df.storge['prescribed_motion_node']
    if any(m.nid == nid and m.dof == dof for m in store.values()):
        raise ValueError(f'Duplicate motion for node {nid}, DOF {dof}')
    cid = max(set(df.define_curve)|set(df.define_table),default=0)+1
    curve = DefineCurve(uid=cid,sfa=1,sfo=1)
    curve.a1,curve.o1 = map(list,zip(*points))
    df.define_curve[cid] = curve
    uid = len(store)+1
    store[uid] = SimpleNamespace(uid=uid,nid=nid,dof=dof,vad=vad,lcid=cid,sf=sf,birth=birth,death=death)


def parse_boundary(options, rows, df, sets, amplitudes, restored=False):
    options = dict(options)
    if options.pop('OP', 'MOD').upper() != 'MOD':
        raise ValueError('BOUNDARY: only OP=MOD loading is supported')
    if set(options)-{'TYPE','AMPLITUDE'}:
        raise ValueError('BOUNDARY: unsupported loading parameters')
    kind = options.get('TYPE','DISPLACEMENT').upper()
    if kind not in ('DISPLACEMENT','VELOCITY','ACCELERATION'):
        raise ValueError(f'BOUNDARY: unsupported type {kind}')
    terms = list(df.control_termination.values())
    end = terms[-1].endtim if terms else 1.0
    for row in rows:
        values = [v.strip().upper() for v in row.split(',')]
        if len(values)<2:
            raise ValueError('BOUNDARY: missing DOF')
        if not values[1].isdecimal():
            if options:
                raise ValueError('BOUNDARY: type-format constraints cannot use loading options')
            from .boundary_parser import BoundaryParser
            BoundaryParser().parse({},[row],df,sets)
            continue
        selected = [int(values[0])] if values[0].isdecimal() else resolve(sets,values[0])
        first = int(values[1]); last = int(values[2]) if len(values)>2 and values[2] else first
        sf = float(values[3]) if len(values)>3 and values[3] else 0.0
        if not 1<=first<=last<=6 or not math.isfinite(sf):
            raise ValueError('BOUNDARY: invalid DOF or loading value')
        points = amplitudes[options['AMPLITUDE'].upper()] if 'AMPLITUDE' in options else [(0.0,0.0),(end,1.0)]
        for nid in selected:
            if nid not in df.node:
                raise ValueError(f'BOUNDARY: missing node {nid}')
            for dof in range(first,last+1):
                if restored and (any(m.nid==nid and m.dof==dof for m in df.storge['prescribed_motion_node'].values()) or
                                 (nid in df.storge['initial_velocity_node'] and df.storge['initial_velocity_node'][nid].components[dof-1])):
                    continue
                if sf == 0 and not options:
                    from .boundary_parser import BoundaryParser
                    BoundaryParser().parse({},[f'{nid},{dof},{dof},0'],df,sets)
                else:
                    add_motion(df,nid,dof,{'DISPLACEMENT':2,'VELOCITY':0,'ACCELERATION':1}[kind],sf,points)
