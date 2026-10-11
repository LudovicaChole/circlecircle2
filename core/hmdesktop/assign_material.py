"""Import complete LS-DYNA catalog templates with collision-free IDs."""
import re
from types import SimpleNamespace
from .tcl_bridge import run, quote, ids, value


class Materials:
    def __init__(self, model, catalog, directory, settings, log):
        self.model, self.directory, self.settings, self.log = model, directory, settings, log
        from core.fea.material_catalog import load_catalog
        self.data = load_catalog(catalog)
        self.cache = {}
        self.tags = set().union(*(set(v) for v in self.data.values())) if self.data else set()

    def suffix(self, name):
        # STEP import may append a numeric CAD occurrence suffix (e.g. .7).
        from .component_names import material_suffix
        return material_suffix(name, self.tags)

    def import_material(self, tag):
        from core.fea.material_cards import READERS
        from core.fea.material_catalog import MaterialCatalog, elastic_material
        key = tag or 'default_elastic'
        if key in self.cache:
            return self.cache[key]
        mid = max(ids('mats'), default=0)+1
        template = self.data.get('lsdyna', {}).get(tag)
        if template:
            material = READERS['lsdyna'](template)[0]
            material.name = key
            renderer = object.__new__(MaterialCatalog)
            renderer.used_ids = set(ids('curves'))
            renderer.next_id = max(renderer.used_ids, default=0)+1
            text = renderer._render_lsdyna(template, material, mid)
        else:
            self.log.warning('No LS-DYNA template for %s; using elastic material (kg/mm/ms).', key)
            material = SimpleNamespace(name=key, rho=self.settings['density'],
                                       e=self.settings['young_modulus'], pr=self.settings['poisson_ratio'])
            # Preserve known base elastic constants for missing HAZ templates.
            base = key.removesuffix('_haz')
            for solver, reader in READERS.items():
                donor = self.data.get(solver, {}).get(base)
                if donor:
                    record = reader(donor.replace('{material_name}', base))[0]
                    material.rho, material.e, material.pr = record.rho, record.e, record.pr
                    break
            text = elastic_material(material, mid, 'lsdyna')
        path = self.directory/(re.sub(r'[^\w.-]', '_', key)+'.k')
        path.write_text('*KEYWORD\n'+text+'*END\n', encoding='utf-8')
        run(f'*feinputwithdata2 "#ls-dyna/dynakey" {quote(path)} 0 0 0 0 0 1 0 1 0')
        if mid not in ids('mats'):
            raise ValueError(f'Material import failed: {key}')
        self.cache[key] = mid
        return mid

    def assign(self, component, tag):
        mid = self.import_material(tag)
        run(f'*setvalue comps id={component} cardimage=Part materialid={{mats {mid}}}')
        if int(value('comps', component, 'materialid')) != mid:
            raise ValueError(f'Failed to assign material {mid} to component {component}')
        return mid
