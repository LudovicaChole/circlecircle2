from core.fea.parser import Parser
from core.fea.lsdyna.keywords.constrained_extra_nodes_set import ConstrainedExtraNodesSet


class ConstrainedExtraNodesSetParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0,
        }

    def _12p0(self, line_raw):
        pid_raw = line_raw[0:10].strip()
        nsid_raw = line_raw[10:20].strip()
        iflag_raw = line_raw[20:30].strip()

        if len(pid_raw) > 0:
            pid = self.dataframe.parameter[pid_raw[1:]].value if pid_raw.startswith("&") else int(pid_raw)
        else:
            pid = 0

        if len(nsid_raw) > 0:
            nsid = self.dataframe.parameter[nsid_raw[1:]].value if nsid_raw.startswith("&") else int(nsid_raw)
        else:
            nsid = 0

        if len(iflag_raw) > 0:
            iflag = self.dataframe.parameter[iflag_raw[1:]].value if iflag_raw.startswith("&") else int(iflag_raw)
        else:
            iflag = 0

        uid = len(self.dataframe.constrained_extra_nodes_set) + 1

        self.dataframe.constrained_extra_nodes_set[uid] = ConstrainedExtraNodesSet(uid=uid,
                                                                                   pid=pid,
                                                                                   nsid=nsid,
                                                                                   iflag=iflag)

        if nsid in self.dataframe.set_node_list:
            self.dataframe.constrained_extra_nodes_set[uid].nset = self.dataframe.set_node_list[nsid]

        return
