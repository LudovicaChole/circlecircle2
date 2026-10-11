from core.fea.translator import Translator


class RunendTranslator(Translator):
    def translate(self, version):
        lines = []
        for obj in self.dataframe.control_termination.values():
            lines += ['RUNEND/\n',f' TIME {obj.endtim:.12g}\n','END_RUNEND\n']
        self.dataframe.output_storge['RUNEND'] = lines
