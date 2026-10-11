from core.fea.translator import Translator
from core.fea.material_catalog import MaterialCatalog, elastic_material


class MaterialTranslator(Translator):
    def translate(self, version, material_mapping=False, material_mapping_file_path=None):
        if self.dataframe.solver == 'abaqus':
            from core.fea.abaqus.parser.mat_static_plastic_parser import MatStaticPlasticParser
            lines = MatStaticPlasticParser().translate('lsdyna', material_mapping, material_mapping_file_path)
        else:
            catalog = MaterialCatalog(material_mapping_file_path, 'lsdyna') if material_mapping else None
            lines = [(catalog.render(material, mid) if catalog else None) or
                     elastic_material(material, mid, 'lsdyna')
                     for mid, material in self.dataframe.material.items()]
        self.dataframe.output_storge['*MATERIAL'] = lines
