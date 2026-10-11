from core.fea.parser import Parser
from core.fea.model.lsdyna.constrained_extra_nodes_set import ConstrainedExtraNodesSet
from core.fea.lsdyna.parser.card_fields import fields, number
from core.fea.validation import required_id
from utilities.logger import logger


class ConstrainedExtraNodesSetParser(Parser):
    def __init__(self, title=False):
        super().__init__()
        self.title = title
        self.version = {'12.0': self._12p0, '13.0': self._12p0, "16.0": self._12p0}

    def _12p0(self, line_raw):
        if self.title and self.line_number == 0:
            self.temp.append(line_raw.strip())
            self.line_number = 1
            return
        pid_raw, nsid_raw, flag_raw = fields(line_raw)[:3]
        if (number(pid_raw, self.dataframe, integer=True) == 0 and
                number(nsid_raw, self.dataframe, integer=True) == 0 and
                number(flag_raw, self.dataframe, integer=True) == 0):
            where = getattr(self, 'source_context', '*CONSTRAINED_EXTRA_NODES_SET')
            logger.warning(f'{where}: PID and NSID are blank/zero; empty extra-node constraint skipped')
            if self.title:
                self.reset()
            return
        pid = required_id(pid_raw, 'PID', self.dataframe)
        nsid = required_id(nsid_raw, 'NSID', self.dataframe)
        iflag = number(flag_raw, self.dataframe, integer=True)
        uid = len(self.dataframe.constrained_extra_nodes_set) + 1
        obj = ConstrainedExtraNodesSet(uid=uid, pid=pid, nsid=nsid, iflag=iflag,
                                       name=self.temp[0] if self.title else 'default')
        obj.source_context = getattr(self, 'source_context', '*CONSTRAINED_EXTRA_NODES_SET')
        if nsid in self.dataframe.set_node_list:
            obj.nset = self.dataframe.set_node_list[nsid]
        self.dataframe.constrained_extra_nodes_set[uid] = obj
        if self.title:
            self.reset()
