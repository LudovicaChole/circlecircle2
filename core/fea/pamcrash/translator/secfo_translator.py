from core.fea.translator import Translator
from .selection import ids, selection, field
from utilities.logger import logger


class SecfoTranslator(Translator):
    def translate(self, version):
        lines = []
        for obj in self.dataframe.database_cross_section_plane_id.values():
            if obj.lenl or obj.lenm or obj.did or obj.itype:
                raise ValueError(f'Section {obj.uid}: rectangular/moving section has no verified SECFO PLANE mapping')
            parts = ids(self.dataframe,self.dataframe.set_part_list[obj.psid].ids) if obj.psid else sorted(self.dataframe.part)
            lines.extend(['SECFO / '+field(obj.uid)+'PLANE   '+field(0)+'\n',f'NAME {obj.name}\n',
                '        '+''.join(field(v) for v in (obj.xct,obj.yct,obj.zct,obj.xch,obj.ych,obj.zch,obj.radius))+'\n'])
            lines.extend(selection('PART',parts))
            lines.append(f'$ Source XHEV/YHEV/ZHEV: {obj.xhev}, {obj.yhev}, {obj.zhev}; no mapped output-axis field.\n')
            logger.warning(f'SECFO {obj.uid}: source in-plane output axes have no mapped PAM field', source=obj)
        self.dataframe.output_storge['SECFO'] = lines
