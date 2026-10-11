from core.fea.translator import Translator
from .card_fields import card, field


class DatabaseCrossSectionSetTranslator(Translator):
    def translate(self, version):
        df, lines = self.dataframe, []
        sid = max([*df.set_node_list,*df.set_shell_list,*df.set_solid_list],default=0)+1
        for obj in df.storge['cross_section_set'].values():
            if set(obj.node_ids)-df.node.keys():
                raise ValueError(f'Section {obj.uid}: missing selected nodes')
            shells = [eid for eid in obj.element_ids if eid in df.element_shell]
            solids = [eid for eid in obj.element_ids if eid in df.element_solid]
            if len(shells)+len(solids)!=len(obj.element_ids):
                raise ValueError(f'Section {obj.uid}: missing/unsupported selected elements')
            nsid = sid
            hsid,ssid = (sid+1 if solids else 0),(sid+2 if shells else 0)
            for keyword, ident, values in (('*SET_NODE_LIST',nsid,obj.node_ids),
                    ('*SET_SOLID_LIST',hsid,solids),('*SET_SHELL_LIST',ssid,shells)):
                if values:
                    lines += [keyword+'\n',card((ident,))]
                    lines += [card(values[i:i+8]) for i in range(0,len(values),8)]
            lines += ['*DATABASE_CROSS_SECTION_SET_ID\n',field(obj.uid,10)+obj.name[:70]+'\n',
                      card((nsid,hsid,0,ssid,0,0,0,0))]
            sid += 3
        df.output_storge['*DATABASE_CROSS_SECTION_SET'] = lines
