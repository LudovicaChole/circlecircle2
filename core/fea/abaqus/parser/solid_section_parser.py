from core.fea.model.lsdyna.section_solid import SectionSolid


class SolidSectionParser:
    def parse(self, options, rows, sid):
        if set(options) - {'ELSET', 'MATERIAL'} or any(r.strip(' ,') for r in rows):
            raise ValueError('SOLID SECTION: only homogeneous 3D solids are supported')
        return SectionSolid(uid=sid, elform=1, name=f'p_solid_{sid}')
