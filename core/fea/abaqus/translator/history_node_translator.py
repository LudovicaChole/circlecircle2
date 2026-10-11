from core.fea.translator import Translator


class HistoryNodeTranslator(Translator):
    """Model node set plus history request embedded by StepTranslator."""

    def __init__(self):
        super().__init__()
        self.version = {"6.14": self._6p14, "2024": self._6p14}
        self.set_name = "dyna_history_nodes"

    def translate(self, version):
        if version in self.version:
            self.version[version]()

    def _6p14(self):
        node_ids = set()
        for history in self.dataframe.database_history_node.values():
            for value in history.ids:
                raw = str(value).strip()
                nid = int(self.dataframe.parameter[raw[1:]].value) if raw.startswith("&") else int(raw)
                if nid == 0:
                    continue
                if nid not in self.dataframe.node:
                    raise ValueError(f"ABAQUS HistoryNodeTranslator ERROR: missing history node {nid}")
                node_ids.add(nid)
        if not node_ids:
            return
        lines = [f"*NSET, NSET={self.set_name}\n"]
        node_ids = sorted(node_ids)
        for start in range(0, len(node_ids), 16):
            lines.append(", ".join(str(nid) for nid in node_ids[start:start + 16]) + "\n")
        self.dataframe.output_storge.setdefault("*NSET_HISTORY", []).extend(lines)
        # History data must be included inside an analysis step.
        self.dataframe.output_history_node[:] = [
            "** Nodal history output\n",
            "*OUTPUT, HISTORY\n",
            f"*NODE OUTPUT, NSET={self.set_name}\n",
            "U, V, A, RF\n",
        ]
