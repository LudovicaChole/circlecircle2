from core.fea.lsdyna.parser.card_fields import fields, number
from core.fea.parser import Parser
from core.fea.model.lsdyna.define_curve import DefineCurve


class DefineCurveTitleParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0, "16.0": self._12p0,
        }

        self.current_curve_id = None

    def _12p0(self, line_raw):
        if not line_raw.strip():
            return
        if self.line_number == 0:
            name_raw = line_raw.strip()

            self.temp.append(name_raw)

            self.line_number = 1

            return

        if self.line_number == 1:
            name_raw = self.temp[0]
            lcid_raw = fields(line_raw)[0]
            sidr_raw = fields(line_raw)[1]
            sfa_raw = fields(line_raw)[2]
            sfo_raw = fields(line_raw)[3]
            offa_raw = fields(line_raw)[4]
            offo_raw = fields(line_raw)[5]
            dattyp_raw = fields(line_raw)[6]
            lcint_raw = fields(line_raw)[7]

            name = name_raw
            lcid = number(lcid_raw, self.dataframe, integer=True)

            if len(sidr_raw) > 0:
                sidr = number(sidr_raw, self.dataframe, integer=True)
            else:
                sidr = 0

            if len(sfa_raw) > 0:
                sfa = number(sfa_raw, self.dataframe, integer=False)
            else:
                sfa = 1.0

            if len(sfo_raw) > 0:
                sfo = number(sfo_raw, self.dataframe, integer=False)
            else:
                sfo = 1.0

            if len(offa_raw) > 0:
                offa = number(offa_raw, self.dataframe, integer=False)
            else:
                offa = 0.0

            if len(offo_raw) > 0:
                offo = number(offo_raw, self.dataframe, integer=False)
            else:
                offo = 0.0

            if len(dattyp_raw) > 0:
                dattyp = number(dattyp_raw, self.dataframe, integer=True)
            else:
                dattyp = 0

            if len(lcint_raw) > 0:
                lcint = number(lcint_raw, self.dataframe, integer=True)
            else:
                lcint = 0

            self.dataframe.define_curve[lcid] = DefineCurve(uid=lcid,
                                                            sidr=sidr,
                                                            sfa=sfa,
                                                            sfo=sfo,
                                                            offa=offa,
                                                            offo=offo,
                                                            dattyp=dattyp,
                                                            lcint=lcint,
                                                            name=name)

            self.current_curve_id = lcid

            self.line_number = 2

            return

        if (self.line_number != 0) and (self.line_number != 1):
            a1_raw = fields(line_raw, (20, 20))[0]
            o1_raw = fields(line_raw, (20, 20))[1]

            if not a1_raw or not o1_raw:
                raise ValueError('DEFINE_CURVE: both abscissa and ordinate are required')
            a1 = number(a1_raw, self.dataframe, integer=False)
            o1 = number(o1_raw, self.dataframe, integer=False)

            self.dataframe.define_curve[self.current_curve_id].a1.append(a1)
            self.dataframe.define_curve[self.current_curve_id].o1.append(o1)

            return
