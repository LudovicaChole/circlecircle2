from core.fea.material_catalog import MaterialCatalog
from core.fea.pamcrash.translator.material_translator import MaterialTranslator


class MaterialMappingTranslator(MaterialTranslator):
    def translate(self, version, material_mapping_file_path):
        material_mapping = MaterialCatalog(material_mapping_file_path, "pamcrash")
        super().translate(version=version, material_mapping=material_mapping)
