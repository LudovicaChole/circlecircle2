from core.fea.parser import Parser
from core.fea.pamcrash.keywords.node import Node


class NodeParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "2020": self._2020,
        }

    def parse(self, line_raw, version):
        """
        :param line_raw: raw data
        :return: Node Object
        """
        try:
            if version in self.version:
                self.version[version](line_raw)

        except Exception as e:
            raise Exception(f"pam-crash version {version} is not supported for NODE keyword\n {e}") from e

    def _2020(self, line_raw):
        nid_raw = line_raw[7:16].strip()
        x_raw = line_raw[16:32].strip()
        y_raw = line_raw[32:48].strip()
        z_raw = line_raw[48:64].strip()

        nid = nid_raw[1:] if nid_raw.startswith("&") else int(nid_raw)
        x = x_raw[1:] if x_raw.startswith("&") else float(x_raw)
        y = y_raw[1:] if y_raw.startswith("&") else float(y_raw)
        z = z_raw[1:] if z_raw.startswith("&") else float(z_raw)

        uid = len(self.dataframe.node) + 1

        self.dataframe.node[uid] = Node(uid=uid,
                                        nid=nid,
                                        x=x,
                                        y=y,
                                        z=z)

        self.dataframe.node_tensor.append([uid, x, y, z])

        self.dataframe.storge_node_id.append(uid)

        self.reset()

