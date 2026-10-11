from core.fea.translator import Translator
from .analysis_data import rigid_dofs


class BoundaryTranslator(Translator):
    def translate(self, version):
        lines = []
        for pid, reference in self.dataframe.storge_rigid_part_reference_node.items():
            material = self.dataframe.material[self.dataframe.part[pid].mid]
            # Keep initial constraints as model data. Step boundary conditions
            # modify them through Abaqus OP=MOD without losing the source mask.
            dofs = rigid_dofs(material)
            if dofs:
                lines.append('*BOUNDARY\n')
                lines.extend(f'{reference}, {dof}, {dof}, 0.0\n' for dof in sorted(dofs))
        for obj in self.dataframe.storge['boundary_spc_node'].values():
            lines.append('*BOUNDARY\n')
            lines.extend(f'{obj.uid}, {dof}, {dof}, 0.0\n' for dof in obj.dofs)
        if lines:
            self.dataframe.output_storge['*BOUNDARY'] = lines
