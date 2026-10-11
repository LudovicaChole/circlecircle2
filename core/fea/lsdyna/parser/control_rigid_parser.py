from core.fea.parser import Parser
from core.fea.model.lsdyna.control_rigid import ControlRigid


class ControlRigidParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0, "16.0": self._12p0,
        }

    def _12p0(self, line_raw):
        lmf_raw = line_raw[0:10].strip()
        jntf_raw = line_raw[10:20].strip()
        orthmd_raw = line_raw[20:30].strip()
        partm_raw = line_raw[30:40].strip()
        sparse_raw = line_raw[40:50].strip()
        metalf_raw = line_raw[50:60].strip()
        plotel_raw = line_raw[60:70].strip()
        rbsms_raw = line_raw[70:80].strip()

        if len(lmf_raw) > 0:
            lmf = self.dataframe.parameter[lmf_raw[1:]].value if lmf_raw.startswith("&") else float(lmf_raw)
        else:
            lmf = 0

        if len(jntf_raw) > 0:
            jntf = self.dataframe.parameter[jntf_raw[1:]].value if jntf_raw.startswith("&") else float(jntf_raw)
        else:
            jntf = 0

        if len(orthmd_raw) > 0:
            orthmd = self.dataframe.parameter[orthmd_raw[1:]].value if orthmd_raw.startswith("&") else float(orthmd_raw)
        else:
            orthmd = 0

        if len(partm_raw) > 0:
            partm = self.dataframe.parameter[partm_raw[1:]].value if partm_raw.startswith("&") else float(partm_raw)
        else:
            partm = 0

        if len(sparse_raw) > 0:
            sparse = self.dataframe.parameter[sparse_raw[1:]].value if sparse_raw.startswith("&") else float(sparse_raw)
        else:
            sparse = 0

        if len(metalf_raw) > 0:
            metalf = self.dataframe.parameter[metalf_raw[1:]].value if metalf_raw.startswith("&") else float(metalf_raw)
        else:
            metalf = 0

        if len(plotel_raw) > 0:
            plotel = self.dataframe.parameter[plotel_raw[1:]].value if plotel_raw.startswith("&") else float(plotel_raw)
        else:
            plotel = 0

        if len(rbsms_raw) > 0:
            rbsms = self.dataframe.parameter[rbsms_raw[1:]].value if rbsms_raw.startswith("&") else float(rbsms_raw)
        else:
            rbsms = 0

        uid = len(self.dataframe.control_rigid) + 1

        self.dataframe.control_rigid[uid] = ControlRigid(uid=uid,
                                                         lmf=lmf,
                                                         jntf=jntf,
                                                         orthmd=orthmd,
                                                         partm=partm,
                                                         sparse_raw=sparse_raw,
                                                         metalf=metalf,
                                                         plotel=plotel,
                                                         rbsms=rbsms)

        return
