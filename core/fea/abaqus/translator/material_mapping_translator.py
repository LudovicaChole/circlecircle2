from core.fea.material_mapping import MaterialMapping
from core.fea.abaqus.translator.material_translator import MaterialTranslator


class MaterialMappingTranslator(MaterialTranslator):
    def translate(self, version, material_mapping_file_path):
        material_mapping = MaterialMapping(material_mapping_file_path, "abaqus")
        super().translate(version=version, material_mapping=material_mapping)
