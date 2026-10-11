from core.fea.translator import Translator
from .selection import ids, selection, group_name


class GroupTranslator(Translator):
    def translate(self, version):
        lines = []
        for family, key, token in [('node','set_node_list','NOD'),('shell','set_shell_list','ELE'),
                                   ('solid','set_solid_list','ELE'),('part','set_part_list','PART')]:
            for sid,obj in self.dataframe.storge.get(key,{}).items():
                values = ids(self.dataframe,obj.ids)
                if not values:
                    continue
                lines.append(f"GROUP / '{group_name(family,sid,obj)}'\n")
                lines.extend(selection(token,values))
        from .selection import resolve
        for sid in self.dataframe.set_segment:
            lines.append(f"GROUP / 'segments_{sid}'\n")
            lines.extend(resolve(self.dataframe, sid, 0))
        lines.extend(self.dataframe.output_storge.pop('MOTION_GROUP', []))
        self.dataframe.output_storge['GROUP'] = lines
