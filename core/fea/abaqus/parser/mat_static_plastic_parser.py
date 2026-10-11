from core.fea.validation import FeaInputError
from pathlib import Path
from core.fea.material_cards import register_materials, read_abaqus
from core.fea.material_catalog import MaterialCatalog, elastic_material
from core.fea.dataframe import dataframe


class MatStaticPlasticParser:
    """Read density/elastic/static plastic cards and convert to either solver."""
    def parse_file(self, file_path):
        try:
            register_materials(Path(file_path).read_text(encoding='utf-8-sig'), 'abaqus', file_path=file_path)
        except (ValueError, IndexError, KeyError) as error:
            raise FeaInputError(f'{file_path}: abaqus material cards: {error}') from error

    def parse_text(self, text):
        return read_abaqus(text)

    def translate(self, solver, material_mapping=False, material_mapping_file_path=None):
        if solver not in ('lsdyna', 'pamcrash'):
            raise ValueError(f'Unsupported target: {solver}')
        catalog = MaterialCatalog(material_mapping_file_path, solver) if material_mapping else None
        return self.render_materials(solver, catalog)

    def render_materials(self, solver, catalog=None):
        """Both reverse writers use the same matching and elastic fallback."""
        return [((catalog.render(material, mid) if catalog else None) or
                 elastic_material(material, mid, solver)) for mid, material in dataframe.material.items()]
