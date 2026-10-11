from core.fea.material_catalog import MaterialCatalog
from core.fea.abaqus.translator.material_translator import MaterialTranslator


class MaterialMappingTranslator(MaterialTranslator):
    def translate(self, version, material_mapping_file_path):
        material_mapping = MaterialCatalog(material_mapping_file_path, "abaqus")
        super().translate(version=version, material_mapping=material_mapping)
