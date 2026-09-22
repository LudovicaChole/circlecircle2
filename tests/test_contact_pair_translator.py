import logging
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

logging.getLogger("user_logger").addHandler(logging.NullHandler())

from core.fea.dataframe import dataframe as data
from core.fea.abaqus.translator.contact_surface import ContactSurface
from core.fea.abaqus.translator.contact_pair_translator import ContactPairTranslator
from core.fea.lsdyna.keywords.element_shell import ElementShell
from core.fea.lsdyna.keywords.element_solid import ElementSolid
from core.fea.lsdyna.keywords.contact_automatic_surface_to_surface_id import ContactAutomaticSurfaceToSurfaceID
from core.fea.lsdyna.parser.contact_automatic_surface_to_surface_id_parser import ContactAutomaticSurfaceToSurfaceIDParser
from core.fea.lsdyna.parser.contact_automatic_surface_to_surface_id_title_parser import ContactAutomaticSurfaceToSurfaceIDTitleParser
from core.fea.lsdyna.parser.set_segment_parser import SetSegmentParser
from core.fea.lsdyna.parser.set_part_list_generate_parser import SetPartListGenerateParser


def read_elsets(text):
    sets, current, generate = {}, None, False
    for line in text.splitlines():
        if line.upper().startswith("*ELSET"):
            current = re.search(r"ELSET\s*=\s*([^,]+)", line, re.I).group(1).strip()
            sets[current] = set()
            generate = "GENERATE" in line.upper()
        elif line.startswith("*"):
            current = None
        elif current and line.strip():
            values = [int(value.strip()) for value in line.split(",") if value.strip()]
            sets[current].update(range(values[0], values[1] + 1, values[2]) if generate else values)
    return sets


class ContactPairTests(unittest.TestCase):
    def setUp(self):
        data.reset()
        self.addCleanup(data.reset)
        self.surface = ContactSurface(data)
        for pid, z in ((1, 0), (2, 1)):
            ids = tuple(pid * 10 + i for i in range(1, 5))
            for uid, xy in zip(ids, ((0, 0), (1, 0), (1, 1), (0, 1))):
                data.node[uid] = SimpleNamespace(xyz=(*xy, z))
            element = ElementShell(uid=pid, pid=pid, **dict(zip(("n1", "n2", "n3", "n4"), ids)))
            data.element_shell[pid] = element
            data.storge_part_element[pid] = [element]
            data.part[pid] = SimpleNamespace(uid=pid)
        data.set_part_list[10] = SimpleNamespace(ids=["2", "2", "0"])
        data.contact_automatic_surface_to_surface_id[7] = ContactAutomaticSurfaceToSurfaceID(
            uid=7, ssid=1, msid=10, sstyp=3, mstyp=2, fs=.1, fd=.3)

    def test_shell_sides_friction_and_defaults(self):
        ContactPairTranslator().translate("6.14")
        text = "".join(data.output_storge["*CONTACT PAIR"])
        self.assertIn("dyna_contact_7_slave_SPOS, SPOS", text)
        self.assertIn("dyna_contact_7_master_SNEG, SNEG", text)
        self.assertIn("*FRICTION\n0.3\n", text)
        self.assertIn("PRESSURE-OVERCLOSURE=HARD", text)
        self.assertIn("ADJUST=0.1, TYPE=SURFACE TO SURFACE", text)
        self.assertTrue(text.endswith("dyna_contact_7_slave, dyna_contact_7_master\n"))

    def test_single_contact_is_ignored(self):
        data.contact_automatic_surface_to_surface_id.clear()
        data.contact_automatic_single_surface_id[1] = object()
        ContactPairTranslator().translate("6.14")
        self.assertNotIn("*CONTACT PAIR", data.output_storge)

    def test_missing_set_does_not_write_partial_contact(self):
        data.set_part_list.clear()
        with self.assertRaisesRegex(ValueError, "contact 7"):
            ContactPairTranslator().translate("6.14")
        self.assertNotIn("*CONTACT PAIR", data.output_storge)

    def test_shell_set_and_segment_set(self):
        data.set_shell_list[5] = SimpleNamespace(ids=["1"])
        self.assertEqual(self.surface.resolve(5, 1)[0][0], 1)
        for title in (False, True):
            parser = SetSegmentParser(title=title)
            if title:
                parser.parse("face set\n", "12.0")
            parser.parse("8\n", "12.0")
            parser.parse("11,12,13,14\n", "12.0")
            self.assertEqual(self.surface.resolve(8, 0)[0][0], 1)

    def test_tetra_exterior_removes_shared_face(self):
        first = ElementSolid(uid=100, pid=1, n1=1, n2=2, n3=3, n4=4, n5=4, n6=4, n7=4, n8=4)
        second = ElementSolid(uid=101, pid=1, n1=1, n2=3, n3=2, n4=5, n5=5, n6=5, n7=5, n8=5)
        faces = self.surface._exterior([first, second])
        self.assertEqual(len(faces), 6)
        self.assertNotIn((100, "S1"), [(uid, side) for uid, side, _ in faces])
        self.assertNotIn((101, "S1"), [(uid, side) for uid, side, _ in faces])

    def test_wedge_face_numbers_follow_exported_connectivity(self):
        wedge = ElementSolid(uid=100, pid=1, n1=1, n2=2, n3=3, n4=4, n5=5, n6=5, n7=7, n8=7)
        faces = {side: set(nodes) for _, side, nodes in self.surface._element_faces(wedge)}
        self.assertEqual(faces["S1"], {1, 5, 2})
        self.assertEqual(faces["S2"], {4, 3, 7})
        self.assertEqual(faces["S3"], {1, 4, 7, 5})
        self.assertEqual(faces["S4"], {5, 7, 3, 2})
        self.assertEqual(faces["S5"], {2, 3, 4, 1})

    def test_hex_and_pyramid_face_numbers(self):
        for fmt, nodes, expected in [
            ("hex8", [1, 2, 3, 4, 5, 6, 7, 8], {"S6": {1, 4, 5, 8}}),
            ("pyramid5", [1, 2, 3, 4, 5, 5, 5, 5], {"S2": {1, 2, 5}, "S5": {1, 4, 5}}),
        ]:
            element = ElementSolid(uid=100, pid=1, **{f"n{i}": node for i, node in enumerate(nodes, 1)})
            self.assertEqual(element.format, fmt)
            actual = {side: set(face) for _, side, face in self.surface._element_faces(element)}
            for side, face in expected.items():
                self.assertEqual(actual[side], face)

    def test_ambiguous_shell_orientation_reports_error(self):
        faces = self.surface.resolve(1, 3)
        with self.assertRaisesRegex(ValueError, "contact side"):
            self.surface.orient_shells(faces, faces)

    def test_parameter_contact_and_optional_cards(self):
        data.parameter["mu"] = SimpleNamespace(value=.45)
        data.parameter["slave"] = SimpleNamespace(value=1)
        for parser in (ContactAutomaticSurfaceToSurfaceIDParser(), ContactAutomaticSurfaceToSurfaceIDTitleParser()):
            parser.reset()
            if isinstance(parser, ContactAutomaticSurfaceToSurfaceIDTitleParser):
                parser.parse("contact title\n", "12.0")
            parser.parse(f"{8:>10}test\n", "12.0")
            parser.parse("".join(f"{v:>10}" for v in ("&slave", 10, 3, 2)) + "\n", "12.0")
            parser.parse(f"{'&mu':>10}{.2:>10}\n", "12.0")
            parser.parse(" " * 80 + "\n", "12.0")
            for _ in range(6):
                parser.parse(" " * 80 + "\n", "12.0")
            self.assertEqual(data.contact_automatic_surface_to_surface_id[8].fs, .45)
            self.assertEqual(data.contact_automatic_surface_to_surface_id[8].ssid, 1)

    def test_multiple_generated_part_ranges(self):
        parser = SetPartListGenerateParser()
        for line in ("99\n", "1 3\n", "6 8\n"):
            parser.parse(line, "12.0")
        self.assertEqual(data.set_part_list[99].ids, [1, 2, 3, 6, 7, 8])

    @unittest.skipUnless(Path(r"E:\PythonProject\test_hwx\abaqus_contact_sample.inp").exists(), "User reference unavailable")
    def test_user_model_matches_reference_faces_in_both_mapping_modes(self):
        from services.fea_keywords_translator import FeaKeywordsTranslator
        reference = Path(r"E:\PythonProject\test_hwx\abaqus_contact_sample.inp").read_text()
        expected = read_elsets(reference)
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "model.k"
            shutil.copyfile(r"E:\PythonProject\circlecircle2\Test_Items\test_model.k", source)
            mapping = Path(__file__).resolve().parents[1] / "Test_Items/material_mapping.json"
            for enabled in (False, True):
                FeaKeywordsTranslator().translate(str(source), "lsdyna", "12.0", "ABAQUS", "6.14", enabled, str(mapping))
                text = source.with_name("model_test.geo").read_text() + source.with_name("model_test.inp").read_text()
                self.assertEqual(text.count("*CONTACT PAIR,"), 2)
                actual = read_elsets(text)
                for side in ("S1", "S2", "S3", "S4"):
                    self.assertEqual(actual[f"dyna_contact_4_master_{side}"], expected[f"_solid_surface_{side}"])
                self.assertEqual(actual["dyna_contact_3_slave_SNEG"], expected["_surface1_SPOS"])
                self.assertEqual(actual["dyna_contact_3_master_SPOS"], expected["_set2_SPOS"])
                self.assertEqual(actual["dyna_contact_4_slave_SNEG"], expected["_surface2_SPOS"])


if __name__ == "__main__":
    unittest.main()
