"""PAM node-surface ties with independent link search distance properties."""
from core.fea.translator import Translator
from .selection import field, selection, resolve


class TieTranslator(Translator):
    def translate(self, version):
        df, lines = self.dataframe, []
        next_pid = max(df.part,default=0)+1
        for index, obj in enumerate(df.storge['surface_ties'].values()):
            if obj.master.sid is None:
                raise ValueError(f'TIE {obj.name}: master must be an element surface')
            pid = next_pid+index
            lines += ['PART  / '+field(pid)+field('TIED')+' '*32+'\n', f'NAME {obj.name}\n',
                      '       0.0       1.0\n',' '*30+'\n',field(obj.tolerance,10)+' '*50+field(0,10)+field(0,10)+'\n',
                      'END_PART\n', 'TIED  / '+field(obj.uid)+field(pid)+field(-1)+field(0)+'\n', f'NAME {obj.name}\n']
            lines.extend(selection('NOD',obj.slave.nodes))
            lines.extend(resolve(df,obj.master.sid,0))
        df.output_storge['TIED'] = lines
