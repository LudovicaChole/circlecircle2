from core.fea.translator import Translator
from core.fea.material_catalog import elastic_material


class MaterialTranslator(Translator):
    def __init__(self):
        super().__init__()
        self.version = {"6.14": self._write, "2024": self._write}

    def translate(self, version, material_mapping=None):
        self._write(material_mapping)

    def _write(self, material_mapping=None):
        lines = []
        for mid, material in self.dataframe.material.items():
            text = material_mapping.render(material, mid) if material_mapping else None
            lines.append(text or elastic_material(material, mid, 'abaqus'))
        self.dataframe.output_storge['*MATERIAL'] = lines
