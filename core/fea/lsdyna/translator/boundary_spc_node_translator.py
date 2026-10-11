from core.fea.translator import Translator
from .card_fields import card


class BoundarySpcNodeTranslator(Translator):
    def translate(self, version):
        store = self.dataframe.storge['boundary_spc_node']
        lines = ['*BOUNDARY_SPC_NODE\n'] if store else []
        lines += [card((obj.uid,0,*(int(i in obj.dofs) for i in range(1,7)))) for obj in store.values()]
        self.dataframe.output_storge['*BOUNDARY_SPC_NODE'] = lines
