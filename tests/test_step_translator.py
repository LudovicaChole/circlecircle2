import logging
import tempfile
import unittest
from pathlib import Path

logging.getLogger("user_logger").addHandler(logging.NullHandler())

from core.fea.abaqus.translator.step_translator import StepTranslator
from core.fea.dataframe import dataframe
from services.fea_keywords_translator import FeaKeywordsTranslator


class StepTranslatorTests(unittest.TestCase):
    def setUp(self):
        dataframe.reset()
        self.addCleanup(dataframe.reset)

    def test_defaults_and_history_placement(self):
        dataframe.output_history_node[:] = ["*OUTPUT, HISTORY\n", "*NODE OUTPUT, NSET=dyna_history_nodes\n", "U, V, A, RF\n"]
        lines = StepTranslator().translate("6.14")
        text = "".join(lines)
        self.assertIn("*STATIC\n0.01, 1.0, 1e-08, 0.1\n", text)
        self.assertLess(text.index("*STEP,"), text.index("*OUTPUT, HISTORY"))
        self.assertLess(text.index("*OUTPUT, HISTORY"), text.index("*END STEP"))
        self.assertFalse(any(line.startswith(("*CLOAD", "*DLOAD", "*DSLOAD")) for line in lines))

    def test_step_without_history_has_no_dangling_include(self):
        self.assertNotIn("*INCLUDE", "".join(StepTranslator().translate("6.14")))

    def test_service_include_chain_and_filename_spaces(self):
        with tempfile.TemporaryDirectory() as folder:
            model = Path(folder) / "my model_test.geo"
            model.write_text("*HEADING\nTest model\n", encoding="utf-8")
            dataframe.output_history_node[:] = ["*OUTPUT, HISTORY\n", "*NODE OUTPUT, NSET=dyna_history_nodes\n", "U, V, A, RF\n"]
            service = FeaKeywordsTranslator()
            service.write_step_file(str(model), "6.14")
            step = model.with_suffix('.inp').read_text()
            self.assertIn('*INCLUDE, INPUT="my model_test.geo"', step)
            self.assertIn('*NODE OUTPUT',step)
            self.assertIn('U, RF',step)
            self.assertNotIn('U, V, A, RF',step)
            self.assertEqual(len(list(Path(folder).iterdir())),2)
            dataframe.reset()
            service.write_step_file(str(model), "6.14")
            self.assertNotIn('*NODE OUTPUT', model.with_suffix('.inp').read_text())


if __name__ == "__main__":
    unittest.main()
