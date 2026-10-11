from core.fea.parser import Parser
from core.fea.model.lsdyna.constrained_nodal_rigid_body import ConstrainedNodalRigidBody


class ConstrainedNodalRigidBodyParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0, "16.0": self._12p0,
        }

    def _12p0(self, line_raw):
        pid_raw = line_raw[0:10].strip()
        cid_raw = line_raw[10:20].strip()
        sid_raw = line_raw[20:30].strip()
        pnode_raw = line_raw[30:40].strip()
        iprt_raw = line_raw[40:50].strip()
        drflag_raw = line_raw[50:60].strip()
        rrflag_raw = line_raw[60:70].strip()

        if len(pid_raw) > 0:
            pid = pid_raw[1:] if pid_raw.startswith("&") else int(pid_raw)
        else:
            pid = 0

        if len(cid_raw) > 0:
            cid = cid_raw[1:] if cid_raw.startswith("&") else int(cid_raw)
        else:
            cid = 0

        if len(sid_raw) > 0:
            sid = sid_raw[1:] if sid_raw.startswith("&") else int(sid_raw)
        else:
            sid = 0

        if len(pnode_raw) > 0:
            pnode = pnode_raw[1:] if pnode_raw.startswith("&") else int(pnode_raw)
        else:
            pnode = 0

        if len(iprt_raw) > 0:
            iprt = iprt_raw[1:] if iprt_raw.startswith("&") else int(iprt_raw)
        else:
            iprt = 0

        if len(drflag_raw) > 0:
            drflag = drflag_raw[1:] if drflag_raw.startswith("&") else int(drflag_raw)
        else:
            drflag = 0

        if len(rrflag_raw) > 0:
            rrflag = rrflag_raw[1:] if rrflag_raw.startswith("&") else int(rrflag_raw)
        else:
            rrflag = 0

        uid = len(self.dataframe.constrained_nodal_rigid_body) + 1

        self.dataframe.constrained_nodal_rigid_body[uid] = ConstrainedNodalRigidBody(uid=uid,
                                                                                     pid=pid,
                                                                                     cid=cid,
                                                                                     sid=sid,
                                                                                     pnode=pnode,
                                                                                     iprt=iprt,
                                                                                     drflag=drflag,
                                                                                     rrflag=rrflag)

        if sid in self.dataframe.set_node_list:
            self.dataframe.constrained_nodal_rigid_body[uid].nset = self.dataframe.set_node_list[sid]

        return
