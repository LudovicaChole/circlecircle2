from core.fea.translator import Translator
from .analysis_data import rigid_dofs, motion_dof


class BoundaryTranslator(Translator):
    def translate(self, version):
        lines = []
        for pid, reference in self.dataframe.storge_rigid_part_reference_node.items():
            material = self.dataframe.material[self.dataframe.part[pid].mid]
            moving = {motion_dof(m) for m in self.dataframe.boundary_prescribed_motion_rigid.values() if m.typeid == pid}
            dofs = rigid_dofs(material) - moving
            if dofs:
                lines.append('*BOUNDARY\n')
                lines.extend(f'{reference}, {dof}, {dof}, 0.0\n' for dof in sorted(dofs))
        if lines:
            self.dataframe.output_storge['*BOUNDARY'] = lines
