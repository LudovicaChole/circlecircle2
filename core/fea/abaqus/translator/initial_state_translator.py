from core.fea.translator import Translator
from .analysis_data import velocity_field


class InitialStateTranslator(Translator):
    def translate(self, version):
        df = self.dataframe
        from .point_mass import point_mass_cards
        lines = point_mass_cards(df)
        velocities = velocity_field(df)
        if velocities:
            import json
            for nid, components in sorted(velocities.items()):
                lines.append('** CIRCLECIRCLE2_INITIAL_VELOCITY ' + json.dumps([nid, list(components)], separators=(',', ':')) + '\n')
        if lines:
            df.output_storge['*INITIAL_STATE'] = lines
