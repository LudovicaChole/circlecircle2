from core.fea.translator import Translator


class NodeTranslator(Translator):
    def __init__(self):
        super().__init__()

        self.version = {
            "6.14": self._6p14, "2024": self._6p14,
        }

    def translate(self, version):
        try:
            if version in self.version:
                self.version[version]()

        except Exception as e:
            raise Exception(f"ABAQUS NodeTranslator ERROR: {e}") from e

    def _6p14(self):
        if len(self.dataframe.node) > 0:
            self.dataframe.output_storge.setdefault("*NODE", [])
            self.dataframe.output_storge["*NODE"].append(f"*NODE\n")

            for node_id, node in self.dataframe.node.items():
                uid = node.uid
                x = node.x
                y = node.y
                z = node.z

                self.dataframe.output_storge["*NODE"].append(f"{uid:<10},{x:17.10f},{y:17.10f},{z:17.10f}\n")
