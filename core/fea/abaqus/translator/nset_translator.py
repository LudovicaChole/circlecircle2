from core.fea.translator import Translator


class NsetTranslator(Translator):
    def translate(self, version):
        lines = []
        for sid, group in self.dataframe.set_node_list.items():
            if not group.ids:
                continue
            lines.append(f'*NSET, NSET=source_nodes_{sid}\n')
            lines += [', '.join(str(n) for n in group.ids[i:i+16])+'\n'
                      for i in range(0,len(group.ids),16)]
        self.dataframe.output_storge['*NSET'] = lines
