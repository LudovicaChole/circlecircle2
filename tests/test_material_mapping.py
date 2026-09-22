import json
import logging
import shutil
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

# Avoid the application's machine-specific log path during isolated tests.
logging.getLogger("user_logger").addHandler(logging.NullHandler())

from core.fea.dataframe import dataframe
from core.fea.material_mapping import MaterialMapping
from core.fea.abaqus.translator.material_mapping_translator import MaterialMappingTranslator as AbaqusMapping
from core.fea.pamcrash.translator.material_mapping_translator import MaterialMappingTranslator as PamMapping
from core.fea.pamcrash.translator.funct_translator import FunctTranslator
from core.fea.lsdyna.material_mapper import MaterialMapper
from services.fea_material_generator import MaterialGenerator


class MaterialMappingTests(unittest.TestCase):
    def setUp(self):
        dataframe.reset()
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.addCleanup(dataframe.reset)
        self.path = Path(self.folder.name) / "material_mapping.json"
        MaterialGenerator().generate(self.path)
        dataframe.define_curve[10] = SimpleNamespace(
            sfa=1, sfo=1, offa=0, offo=0, a1=[0, .1], o1=[100, 200], name="original")
        for mid, name, tag in [(1, "matched", "minth_s620"), (2, "unknown", None),
                               (3, " MINTH_S624 ", None), (4, "another", "minth_s620")]:
            dataframe.material[mid] = SimpleNamespace(
                name=name, map_tag=tag, tag="plastic", lcss=10, rho=2.7e-6, e=70, pr=.3)
            dataframe.part[mid] = SimpleNamespace(mid=mid, secid=1)
        dataframe.part[5] = SimpleNamespace(mid=1, secid=1)

    def test_abaqus_mapping_and_fallback(self):
        AbaqusMapping().translate("6.14", self.path)
        output = "".join(dataframe.output_storge["*MATERIAL"])
        self.assertEqual(output.count("*MATERIAL, NAME="), 4)
        self.assertIn("201.2, 0.01", output)
        self.assertIn("241.2, 0.02", output)
        self.assertIn("*MATERIAL, NAME=unknown", output)
        self.assertIn("100", output)
        self.assertNotIn("{material_", output)

    def test_pam_mapping_preserves_references_and_original_curves(self):
        PamMapping().translate("2020", self.path)
        FunctTranslator().translate("2020")
        output = "".join(dataframe.output_storge["MATER"])
        ids = [int(line[7:16]) for line in output.splitlines() if line.startswith("MATER /")]
        self.assertEqual(ids, [1, 2, 3, 4])
        curve_ids = [int(line[7:16]) for line in output.splitlines() if line.startswith("FUNCT /")]
        self.assertEqual(len(set(curve_ids)), 3)
        self.assertNotIn(10, curve_ids)
        lines = output.splitlines()
        refs = [int(lines[i + 1][:10]) for i, line in enumerate(lines) if "LC1" in line.split()]
        self.assertEqual(refs, [curve_ids[0], 10, curve_ids[1], curve_ids[2]])
        self.assertIn("FUNCT /       10", "".join(dataframe.output_storge["FUNCT"]))

    def test_directory_and_name_match(self):
        mapping = MaterialMapping(self.folder.name, "abaqus")
        self.assertIn("241.2, 0.02", mapping.render(dataframe.material[3], 3))

    def test_disabled_mapping_uses_standard_translation(self):
        from core.fea.abaqus.translator.material_translator import MaterialTranslator
        MaterialTranslator().translate("6.14")
        self.assertNotIn("201.2", "".join(dataframe.output_storge["*MATERIAL"]))

    def test_standard_plastic_columns_are_stress_then_strain(self):
        from core.fea.abaqus.translator.material_translator import MaterialTranslator
        lines = []
        MaterialTranslator().combine_curve_data(10, dataframe.define_curve, lines)
        first = [float(value.strip()) for value in lines[1].split(",")]
        self.assertEqual(first, [100, 0])

    def test_generated_plastic_columns_are_stress_then_strain(self):
        for template in MaterialGenerator().abaqus_material.values():
            first = template.split("*PLASTIC\n")[1].splitlines()[0]
            stress, strain = [float(value.strip()) for value in first.split(",")[:2]]
            self.assertGreater(stress, 0)
            self.assertEqual(strain, 0)

    def test_invalid_configuration(self):
        with self.assertRaises(ValueError):
            MaterialMapping(None, "abaqus")
        with self.assertRaises(FileNotFoundError):
            MaterialMapping(self.path.with_name("missing.json"), "abaqus")
        self.path.write_text('{"abaqus": []}', encoding="utf-8")
        with self.assertRaises(ValueError):
            MaterialMapping(self.path, "abaqus")
        self.path.write_text('broken', encoding="utf-8")
        with self.assertRaises(json.JSONDecodeError):
            MaterialMapping(self.path, "abaqus")

    def test_service_converts_real_model_with_mapping_on_and_off(self):
        from services.fea_keywords_translator import FeaKeywordsTranslator
        root = Path(__file__).resolve().parents[1]
        source = Path(self.folder.name) / "model.k"
        shutil.copyfile(root / "Test_Items/test_model.k", source)
        for solver, version, extension in [("abaqus", "6.14", ".geo"),
                                            ("PamCrash", "2020", ".inc")]:
            for enabled in (True, False):
                with self.subTest(solver=solver, mapping=enabled):
                    translator = FeaKeywordsTranslator()
                    translator.translate(file_path=str(source), solver1="Ls-Dyna", version1="12.0",
                                         solver2=solver, version2=version,
                                         material_mapping=enabled,
                                         material_mapping_file_path=str(self.path) if enabled else "missing.json")
                    output = source.with_name("model_test" + extension).read_text(encoding="utf-8")
                    self.assertTrue(output)
                    self.assertNotIn("{material_", output)
                    if extension == ".geo":
                        self.assertEqual("201.2, 0.01" in output, enabled)
                    else:
                        lines = output.splitlines()
                        function_ids = [int(line[7:16]) for line in lines if line.startswith("FUNCT /")]
                        self.assertEqual(len(function_ids), len(set(function_ids)))
                        material_ids = {int(line[7:16]) for line in lines if line.startswith("MATER /")}
                        part_material_ids = {int(line[24:32]) for line in lines if line.startswith("PART  /")}
                        self.assertTrue(part_material_ids <= material_ids)

    def test_short_curve_is_not_a_known_material(self):
        self.assertIsNone(MaterialMapper().map_material(10))

    def test_existing_curve_recognition(self):
        dataframe.define_curve[10].a1 = [0, .0001, .0002, .0003, .0004]
        dataframe.define_curve[10].o1 = [.19197, .20039, .20303, .20545, .20696]
        self.assertEqual(MaterialMapper().map_material(10), "minth_s620")


if __name__ == "__main__":
    unittest.main()
