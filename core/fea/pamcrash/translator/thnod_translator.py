from core.fea.translator import Translator
from .selection import ids, selection, field


class ThnodTranslator(Translator):
    def translate(self, version):
        lines = []
        for uid,obj in self.dataframe.database_history_node.items():
            values = ids(self.dataframe,obj.ids)
            if any(n not in self.dataframe.node for n in values):
                raise ValueError(f'History {uid}: missing nodes')
            if values:
                lines.extend(['THNOD / '+field(0)+'\n',f'NAME {obj.name}\n'])
                lines.extend(selection('NOD',values))
        self.dataframe.output_storge['THNOD'] = lines
