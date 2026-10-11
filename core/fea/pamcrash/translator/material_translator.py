from core.fea.translator import Translator
from core.fea.material_catalog import elastic_material


class MaterialTranslator(Translator):
    def __init__(self):
        super().__init__()
        self.version = {"2020": self._write, "2023": self._write}

    def translate(self, version, material_mapping=None):
        self._write(material_mapping)

    def _write(self, material_mapping=None):
        lines = []
        for mid, material in self.dataframe.material.items():
            if mid in self.dataframe.storge_pam_elastic_solid_material:
                continue
            text = material_mapping.render(material, mid) if material_mapping else None
            lines.append(text or elastic_material(material, mid, 'pamcrash'))
        for mid, material in self.dataframe.storge_pam_elastic_solid_material.items():
            text = material_mapping.render(material, mid) if material_mapping else None
            if text:
                headers = [line for line in text.splitlines() if line.startswith('MATER /')]
                if len(headers) != 1:
                    raise ValueError(f'Material {mid}: expected exactly one PAM MATER template')
                matyp = int(headers[0][16:24])
                if matyp not in (100, 105):
                    lines.append(text)
                    continue
                from utilities.logger import logger
                logger.warning(f'Material {mid} ({material.name}): PAM MATYP{matyp} is a shell material; using solid elastic MATYP1', source=material)
            lines.append(elastic_material(material, mid, 'pamcrash', solid=True))
        from core.fea.hourglass_notes import restore_pam_material
        from core.fea.material_cards import pam_blocks
        lines = [restore_pam_material(self.dataframe, text,
                 next(int(rows[0][8:16]) for key, rows in pam_blocks(text) if key == 'MATER /'))
                 for text in lines]
        self.dataframe.output_storge['MATER'] = lines
