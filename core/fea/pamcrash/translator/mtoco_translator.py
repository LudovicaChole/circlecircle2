from core.fea.translator import Translator
from core.fea.model.lsdyna.node import Node
from core.fea.abaqus.translator.analysis_data import rigid_dofs
from .selection import ids, field, selection
from .motion_translator import rigid_motion_dofs


class MtocoTranslator(Translator):
    """Columns follow HyperMesh PAM elements_mtoco_2016 and loads_2016."""
    def translate(self, version):
        df = self.dataframe
        lines, boundaries, used, ownership = [], [], set(), {}

        def emit(uid, reference, nodes, name, dofs=tuple(range(1,7))):
            nodes = sorted(set(nodes) - {reference})
            if reference not in df.node or any(n not in df.node for n in nodes):
                raise ValueError(f'MTOCO {uid}: missing nodes')
            if not nodes:
                raise ValueError(f'MTOCO {uid}: empty dependent node selection')
            for nid in nodes:
                if nid in ownership:
                    raise ValueError(f'MTOCO {uid}: node {nid} already belongs to MTOCO {ownership[nid]}')
                ownership[nid] = uid
            used.add(uid)
            lines.extend(['MTOCO / ' + field(uid) + field(reference) + '  ' + ''.join('1' if i in dofs else '0' for i in range(1,7)) + ' '*8 + field(0) + '\n',
                          f'NAME {name}\n'])
            lines.extend(selection('NOD', nodes))

        for body in df.constrained_nodal_rigid_body.values():
            if body.cid or ((body.drflag or body.rrflag) and not hasattr(body, 'coupled_dofs')):
                raise ValueError(f'Rigid body {body.uid}: local/released constraints require manual MTOCO mapping')
            nodes = ids(df, df.set_node_list[body.sid].ids)
            if not nodes:
                raise ValueError(f'Rigid body {body.uid}: empty node set')
            uid = body.pid
            while uid in used:
                uid += 1
            emit(uid, body.pnode or nodes[0], nodes, body.name, getattr(body, 'coupled_dofs', tuple(range(1,7))))
            df.storge_rigid_part_reference_node[body.pid] = body.pnode or nodes[0]

        for pid, part in df.part.items():
            material = df.material[part.mid]
            if material.tag != 'rigid':
                continue
            nodes = set(df.storge_part_node_id.get(pid, []))
            for extra in df.constrained_extra_nodes_set.values():
                if extra.pid == pid:
                    nodes.update(ids(df, df.set_node_list[extra.nsid].ids))
            if not nodes:
                raise ValueError(f'MAT20 part {pid}: no nodes')
            uid = pid
            while uid in used:
                uid += 1
            # Use a dedicated reference, as in the Abaqus rigid-body writer;
            # never constrain an arbitrary dependent mesh node.
            reference = max(df.node, default=0) + 1
            points = [df.node[nid].xyz for nid in sorted(nodes)]
            center = ((part.xc, part.yc, part.zc) if getattr(part, 'tm', 0) else
                      tuple(sum(p[i] for p in points)/len(points) for i in range(3)))
            df.node[reference] = Node(uid=reference, x=center[0], y=center[1], z=center[2])
            df.output_storge.setdefault('NODE', []).append('NODE  / ' + field(reference) +
                ''.join(field(v, 16) for v in center) + '\n')
            df.storge_rigid_part_reference_node[pid] = reference
            emit(uid, reference, nodes, part.name)
            # Keep the original MAT20 card in the source archive; PAM fixed
            # boundaries must not suppress an imposed motion on the reference.
            dofs = set(rigid_dofs(material)) - rigid_motion_dofs(df, pid)
            if dofs:
                mask = ''.join('1' if d in dofs else '0' for d in range(1, 7))
                boundaries.extend(['BOUNC / ' + field(reference) + '  ' + mask + field(0) + field(0) + '\n',
                                   f'NAME MAT20_{material.uid}_part_{pid}\n'])
        df.output_storge['MTOCO'] = lines
        df.output_storge['BOUNC'] = boundaries
