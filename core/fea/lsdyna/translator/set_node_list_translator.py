from core.fea.translator import Translator
from .card_fields import card


class SetNodeListTranslator(Translator):
    def translate(self, version):
        lines = []
        for s in self.dataframe.set_node_list.values():
            lines += ['*SET_NODE_LIST_TITLE\n', s.name+'\n', card((s.uid,))]
            lines += [card(s.ids[i:i+8]) for i in range(0,len(s.ids),8)]
        self.dataframe.output_storge['*SET_NODE_LIST'] = lines
