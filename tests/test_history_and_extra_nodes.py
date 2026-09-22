import logging
import shutil
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace as Obj

logging.getLogger("user_logger").addHandler(logging.NullHandler())

from core.fea.dataframe import dataframe as data
from core.fea.abaqus.translator.history_node_translator import HistoryNodeTranslator
from core.fea.abaqus.translator.kinematic_coupling_translator import KinematicCouplingTranslator
from core.fea.lsdyna.parser.database_history_node_parser import DatabaseHistoryNodeParser
from core.fea.lsdyna.parser.database_history_node_title_parser import DatabaseHistoryNodeTitleParser
from core.fea.lsdyna.parser.constrained_extra_nodes_set_parser import ConstrainedExtraNodesSetParser
from services.fea_keywords_translator import FeaKeywordsTranslator


def coupling_nodes(lines):
    result, reference = {}, None
    for line in lines:
        if line.startswith("*KINEMATIC COUPLING"):
            reference = int(line.split("=")[1])
            result[reference] = []
        elif reference is not None:
            result[reference].append(int(line.split(",")[0]))
    return result


class HistoryAndExtraNodesTests(unittest.TestCase):
    def setUp(self):
        data.reset()
        self.addCleanup(data.reset)
        for nid, xyz in enumerate(((0, 0, 0), (1, 0, 0), (0, 1, 0), (2, 2, 0), (3, 3, 0)), 1):
            data.node[nid] = Obj(uid=nid, xyz=xyz)
        data.material[20] = Obj(tag="rigid", con1=7, con2=0)
        data.part[100] = Obj(mid=20)
        data.storge_part_node_id[100] = {1, 2, 3}
        data.set_node_list[12] = Obj(ids=["3", "4", "4", "0"])
        data.constrained_extra_nodes_set[1] = Obj(pid=100, nsid=12, iflag=0)

    def test_extra_nodes_share_existing_reference_and_are_unique(self):
        KinematicCouplingTranslator().translate("6.14")
        ref = data.storge_rigid_part_reference_node[100]
        self.assertEqual(ref, 6)
        self.assertEqual(coupling_nodes(data.output_storge["*KINEMATIC"])[ref], [1, 2, 3, 4])
        self.assertEqual(data.storge_rigid_part_goc_xyz[ref], (1 / 3, 1 / 3, 0))
        self.assertEqual(data.storge_rigid_part_goc_con[ref], (7, 0))

    def test_missing_extra_set_fails_without_partial_output(self):
        data.set_node_list.clear()
        with self.assertRaisesRegex(ValueError, "missing extra node set"):
            KinematicCouplingTranslator().translate("6.14")
        self.assertEqual(data.output_storge, {})

    def test_extra_nodes_cannot_target_nonrigid_part(self):
        data.material[20].tag = "elastic"
        with self.assertRaisesRegex(ValueError, "no MAT20"):
            KinematicCouplingTranslator().translate("6.14")

    def test_duplicate_rigid_ownership_is_rejected(self):
        data.part[101] = Obj(mid=20)
        data.storge_part_node_id[101] = {4, 5}
        with self.assertRaisesRegex(ValueError, "different reference"):
            KinematicCouplingTranslator().translate("6.14")

    def test_rigid_body_with_three_noncollinear_shared_nodes_is_flattened(self):
        data.set_node_list[13] = Obj(ids=[5, 1, 2, 3])
        data.constrained_nodal_rigid_body[1] = Obj(uid=1, sid=13, pnode=5)
        KinematicCouplingTranslator().translate("6.14")
        self.assertEqual(coupling_nodes(data.output_storge["*KINEMATIC"]), {6: [1, 2, 3, 4, 5]})

    def test_collinear_shared_nodes_do_not_merge(self):
        for nid in (1, 2, 3):
            data.node[nid].xyz = (nid, 0, 0)
        self.assertFalse(KinematicCouplingTranslator()._fixes_rigid_motion({1, 2, 3}))

    def test_explicit_nodal_reference_is_used(self):
        data.part.clear()
        data.constrained_extra_nodes_set.clear()
        data.set_node_list[13] = Obj(ids=[1, 2, 3])
        data.constrained_nodal_rigid_body[1] = Obj(uid=1, sid=13, pnode=5)
        KinematicCouplingTranslator().translate("6.14")
        self.assertEqual(coupling_nodes(data.output_storge["*KINEMATIC"]), {5: [1, 2, 3]})
        self.assertNotIn("*NODE", data.output_storge)

    def test_extra_node_parameter_references_are_resolved(self):
        data.parameter["part"] = Obj(value=100)
        data.parameter["set"] = Obj(value=12)
        ConstrainedExtraNodesSetParser().parse(f"{'&part':>10}{'&set':>10}{0:>10}\n", "12.0")
        extra = data.constrained_extra_nodes_set[2]
        self.assertEqual((extra.pid, extra.nsid), (100, 12))

    def test_history_collects_all_blocks_and_deduplicates(self):
        parser = DatabaseHistoryNodeParser()
        parser.parse("1,2,0\n", "12.0")
        parser.reset()
        parser.parse(f"{2:>10}{3:>10}\n", "12.0")
        title = DatabaseHistoryNodeTitleParser()
        for nid in (4, 5):
            title.reset()
            title.parse("same title\n", "12.0")
            title.parse(str(nid) + "\n", "12.0")
        HistoryNodeTranslator().translate("6.14")
        self.assertIn("1, 2, 3, 4, 5\n", data.output_storge["*NSET_HISTORY"])
        self.assertNotIn("*OUTPUT, HISTORY", "".join(sum(data.output_storge.values(), [])))
        self.assertIn("U, V, A, RF\n", data.output_history_node)

    def test_history_fixed_width_adjacent_ids(self):
        parser = DatabaseHistoryNodeParser()
        parser.parse("12345678901234567891\n", "12.0")
        self.assertEqual(data.database_history_node[1].ids, ["1234567890", "1234567891"])

    def test_history_missing_node_is_not_silently_dropped(self):
        data.database_history_node[1] = Obj(ids=[999])
        with self.assertRaisesRegex(ValueError, "missing history node 999"):
            HistoryNodeTranslator().translate("6.14")

    def test_reset_clears_history_and_part_reference_mapping(self):
        data.output_history_node.append("old")
        data.storge_rigid_part_reference_node[100] = 6
        data.reset()
        self.assertFalse(data.output_history_node)
        self.assertFalse(data.storge_rigid_part_reference_node)

    def test_reference_model_complete_conversion(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "test_model.k"
            shutil.copyfile(root / "Test_Items/test_model.k", source)
            for enabled in (False, True):
                FeaKeywordsTranslator().translate(str(source), "lsdyna", "12.0", "abaqus", "6.14",
                                                  enabled, str(root / "Test_Items/material_mapping.json"))
                model = source.with_name("test_model_test.geo").read_text()
                step = source.with_name("test_model_test.inp").read_text()
                self.assertIn('*INCLUDE, INPUT="test_model_test.geo"', step)
                self.assertLess(step.index("*STEP,"), step.index("*OUTPUT, HISTORY"))
                self.assertLess(step.index("*OUTPUT, HISTORY"), step.index("*END STEP"))
                self.assertNotIn("*OUTPUT, HISTORY", model)
                self.assertIn("*NODE OUTPUT, NSET=dyna_history_nodes", step)
                self.assertEqual({p.suffix for p in Path(folder).iterdir() if p != source}, {'.geo','.inp'})
                expected = {int(nid) for block in data.database_history_node.values() for nid in block.ids if int(nid)}
                actual = {int(nid) for line in data.output_storge["*NSET_HISTORY"][1:] for nid in line.split(",")}
                self.assertEqual(actual, expected)
                ref = data.storge_rigid_part_reference_node[1800070]
                groups = coupling_nodes(data.output_storge["*KINEMATIC"])
                extra = set(map(int, data.set_node_list[12].ids))
                self.assertTrue(extra <= set(groups[ref]))
                all_slaves = [nid for nodes in groups.values() for nid in nodes]
                self.assertEqual(len(all_slaves), len(set(all_slaves)))


if __name__ == "__main__":
    unittest.main()
