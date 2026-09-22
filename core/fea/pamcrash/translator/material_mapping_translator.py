from core.fea.material_mapping import MaterialMapping
from core.fea.pamcrash.translator.material_translator import MaterialTranslator


class MaterialMappingTranslator(MaterialTranslator):
    def translate(self, version, material_mapping_file_path):
        material_mapping = MaterialMapping(material_mapping_file_path, "pamcrash")
        super().translate(version=version, material_mapping=material_mapping)
