from core.fea.translator import Translator
from .analysis_data import velocity_field


class InitialStateTranslator(Translator):
    def translate(self, version):
        df = self.dataframe
        lines = []
        used = set(df.element_shell) | set(df.element_solid)
        next_id = max(used | set(df.storge.get('element_mass', {})), default=0) + 1
        for mass in df.storge.get('element_mass', {}).values():
            if mass.nid not in df.node:
                raise ValueError(f'ELEMENT_MASS {mass.uid}: missing node {mass.nid}')
            eid = mass.uid
            if eid in used:
                eid, next_id = next_id, next_id+1
            used.add(eid)
            lines += [f'*ELEMENT, TYPE=MASS, ELSET=dyna_mass_{eid}\n',f'{eid}, {mass.nid}\n',
                      f'*MASS, ELSET=dyna_mass_{eid}\n', f'{mass.mass:.12g}\n']
        velocities = velocity_field(df)
        if velocities:
            rotational_nodes = set(df.storge_rigid_part_goc_xyz)
            for element in df.element_shell.values():
                rotational_nodes.update(getattr(element,f'n{i}',0) for i in range(1,5))
            lines.append('*INITIAL CONDITIONS, TYPE=VELOCITY\n')
            for nid, components in sorted(velocities.items()):
                for dof,value in enumerate(components,1):
                    if dof <= 3 or (value and nid in rotational_nodes):
                        lines.append(f'{nid}, {dof}, {value:.12g}\n')
        if lines:
            df.output_storge['*INITIAL_STATE'] = lines
