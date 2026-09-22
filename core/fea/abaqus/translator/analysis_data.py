"""Analysis data shared by model and step writers (consistent source units)."""
import math
from utilities.logger import logger


def is_explicit(df):
    return bool(df.initial_velocity_generation or df.boundary_prescribed_motion_rigid)


def curve_points(curve):
    # R12 Vol I, DEFINE_CURVE remark 2: offsets precede scaling.
    points = [((float(x) + curve.offa) * (curve.sfa or 1.0), (float(y) + curve.offo) * (curve.sfo or 1.0))
              for x, y in zip(curve.a1, curve.o1)]
    if getattr(curve, 'dattyp', 0) == 0 and curve.offa > 0 and points and points[0][0] > 0:
        offset = curve.offa * (curve.sfa or 1.0)
        points = [(0.0, 0.0), (0.999*offset, 0.0)] + points
    if not points or any(b[0] <= a[0] for a, b in zip(points, points[1:])):
        raise ValueError(f'Curve {curve.uid}: time points must strictly increase')
    return points


def rigid_dofs(material):
    cmo = getattr(material, 'cmo', 0)
    if cmo == 0:
        return set()
    if cmo == -1 and material.con1 == 0:
        digits = f'{material.con2:06d}'
        if len(digits) != 6 or set(digits) - {'0','1'}:
            raise ValueError(f'MAT20 {material.uid}: invalid local constraint mask {digits}')
        return {i+1 for i,value in enumerate(digits) if value == '1'}
    if cmo != 1:
        raise ValueError(f'MAT20 {material.uid}: local CMO={cmo} requires coordinate-system conversion')
    codes = {0: (), 1: (1,), 2: (2,), 3: (3,), 4: (1, 2), 5: (2, 3), 6: (1, 3), 7: (1, 2, 3)}
    return set(codes[material.con1]) | {d + 3 for d in codes[material.con2]}


def motion_dof(motion):
    mapping = {1: 1, 2: 2, 3: 3, 5: 4, 6: 5, 7: 6}
    if motion.dof not in mapping:
        raise ValueError(f'Rigid motion {motion.uid}: DOF={motion.dof} requires vector/offset conversion')
    return mapping[motion.dof]


def node_ids(df, values):
    ids = {int(df.parameter[str(v)[1:]].value) if str(v).startswith('&') else int(v) for v in values}
    ids.discard(0)
    missing = ids - df.node.keys()
    if missing:
        raise ValueError(f'Missing selected nodes: {sorted(missing)[:8]}')
    return ids


def velocity_field(df):
    result = {}
    for velocity in df.initial_velocity_generation.values():
        if velocity.lcid:
            raise ValueError(f'Initial velocity {velocity.uid}: local ICID={velocity.lcid} is not supported')
        if velocity.phase:
            raise ValueError('Initial velocity PHASE=1 requires dynamic relaxation geometry')
        parts = set()
        if velocity.pid == 0:
            selected, parts = set(df.node), set(df.part)
        elif velocity.styp in (1, 2):
            if velocity.styp == 1 and velocity.pid not in df.set_part_list:
                raise ValueError(f'Initial velocity {velocity.uid}: missing SET_PART {velocity.pid} (STYP=1)')
            parts = {int(v) for v in df.set_part_list[velocity.pid].ids} if velocity.styp == 1 else {velocity.pid}
            selected = set()
            for pid in parts:
                if pid not in df.part:
                    raise ValueError(f'Initial velocity: missing part {pid}')
                selected.update(node_ids(df, df.storge_part_node_id.get(pid, [])))
        elif velocity.styp == 3:
            selected = node_ids(df, df.set_node_list[velocity.pid].ids)
        else:
            raise ValueError(f'Unsupported initial velocity STYP={velocity.styp}')
        if velocity.ivant:
            for extra in df.constrained_extra_nodes_set.values():
                if extra.pid in parts:
                    selected.update(node_ids(df, df.set_node_list[extra.nsid].ids))
        for pid in parts:
            ref = df.storge_rigid_part_reference_node.get(pid)
            if ref:
                selected.add(ref)
        if not selected:
            raise ValueError(f'Initial velocity {velocity.uid}: selection is empty')
        axis = (velocity.nx, velocity.ny, velocity.nz)
        center = (velocity.xc, velocity.yc, velocity.zc)
        if velocity.nx == -999:
            center = df.node[int(velocity.ny)].xyz
            end = df.node[int(velocity.nz)].xyz
            axis = tuple(b-a for a,b in zip(center,end))
        length = math.sqrt(sum(v*v for v in axis))
        if velocity.omega and length == 0:
            raise ValueError('Initial angular velocity has a zero rotation axis')
        omega = tuple(velocity.omega*v/length if length else 0.0 for v in axis)
        for nid in selected:
            point = df.node[nid].xyz if nid in df.node else df.storge_rigid_part_goc_xyz[nid]
            x,y,z = (b-a for a,b in zip(center,point))
            wx,wy,wz = omega
            result[nid] = (velocity.vx + wy*z-wz*y, velocity.vy + wz*x-wx*z, velocity.vz + wx*y-wy*x, *omega)
    return result


def period(df, default=1.0):
    terms = list(df.control_termination.values())
    if terms:
        value = terms[-1].endtim
        if value <= 0:
            raise ValueError('CONTROL_TERMINATION ENDTIM must be positive')
        return value
    if is_explicit(df):
        logger.warning('No CONTROL_TERMINATION: using explicit duration 1.0 in source model units')
    return default
