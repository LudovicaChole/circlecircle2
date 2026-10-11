"""Represent full Abaqus component couplings with MAT20 and extra node sets.

Only the unique fully captured component becomes rigid. Captured nodes outside
that component retain their original element materials. Partial couplings keep
their nodal representation because a rigid part would overconstrain them.
"""
import copy
from types import SimpleNamespace
from core.fea.model.lsdyna.set_node_list import SetNodeList
from core.fea.model.lsdyna.constrained_extra_nodes_set import ConstrainedExtraNodesSet

CODES = {frozenset(v): k for k, v in {0: (), 1: (1,), 2: (2,), 3: (3,),
         4: (1, 2), 5: (2, 3), 6: (1, 3), 7: (1, 2, 3)}.items()}
MOTION_DOF = {1: 1, 2: 2, 3: 3, 4: 5, 5: 6, 6: 7}


def prepare(df, target):
    if df.solver != 'abaqus' or target != 'lsdyna':
        return
    owners = {}
    for body in df.constrained_nodal_rigid_body.values():
        if getattr(body, 'material_rigidized', False) or getattr(body,'coupled_dofs',set()) != {1,2,3,4,5,6}:
            continue
        selected = set(df.set_node_list[body.sid].ids)
        reference = body.pnode
        candidates = [(pid, part, set(df.storge_part_node_id.get(pid, ()))) for pid, part in df.part.items()]
        candidates = [(pid, part, nodes) for pid, part, nodes in candidates
                      if nodes and nodes <= selected and df.material[part.mid].tag in ('elastic', 'rigid')]
        if len(candidates) != 1:
            continue
        pid, part, nodes = candidates[0]
        if pid in owners:
            raise ValueError(f'Part {pid}: multiple full rigid couplings cannot share a MAT20 part')
        owners[pid] = reference
        motions = [(uid, m) for uid, m in df.storge['prescribed_motion_node'].items() if m.nid == reference]
        fixed = set(getattr(df.storge['boundary_spc_node'].get(reference), 'dofs', ()))
        # The model constraint mask and step prescribed motion are independent
        # source data. Keep both when representing the coupling with MAT20.
        material = copy.copy(df.material[part.mid])
        mid = max(df.material,default=0)+1
        material.uid, material.tag, material.map_tag = mid, 'rigid', None
        material.name = f'{material.name}_rigid_part_{pid}'
        material.cmo = 1 if fixed else 0
        material.con1 = CODES[frozenset(fixed & {1,2,3})]
        material.con2 = CODES[frozenset(d-3 for d in fixed if d>3)]
        df.material[mid] = material
        part.mid = mid
        # MAT20 owns these rigid reference constraints. Do not write them again
        # as BOUNDARY_SPC on an extra node belonging to this rigid part.
        df.storge['boundary_spc_node'].pop(reference, None)
        extra = selected - nodes
        if extra:
            sid = max(df.set_node_list,default=0)+1
            group = SetNodeList(uid=sid,name=f'rigid_extra_nodes_{pid}')
            group.ids = sorted(extra)
            df.set_node_list[sid] = group
            uid = max(df.constrained_extra_nodes_set,default=0)+1
            df.constrained_extra_nodes_set[uid] = ConstrainedExtraNodesSet(uid=uid,pid=pid,nsid=sid,iflag=0)
        for uid, motion in motions:
            rid = max(df.boundary_prescribed_motion_rigid,default=0)+1
            df.boundary_prescribed_motion_rigid[rid] = SimpleNamespace(
                uid=rid,typeid=pid,dof=MOTION_DOF[motion.dof],vad=motion.vad,
                lcid=motion.lcid,sf=motion.sf,vid=0,birth=motion.birth,death=motion.death)
            del df.storge['prescribed_motion_node'][uid]
        body.material_rigidized = True
