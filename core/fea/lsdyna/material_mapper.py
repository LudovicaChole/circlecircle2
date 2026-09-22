from core.fea.dataframe import dataframe


class MaterialMapper:
    def __init__(self):
        self.dataframe = dataframe
        self.num = 0

    def get_curve_info(self, curve_id):
        if curve_id in self.dataframe.define_curve:
            curve = self.dataframe.define_curve[curve_id]

            sfa = curve.sfa
            sfo = curve.sfo
            offa = curve.offa
            offo = curve.offo
            a1 = curve.a1
            o1 = curve.o1

            if min(len(a1), len(o1)) < 5:
                return (0,) * 10

            x1 = round((a1[0] - offa) * sfa, 10)
            x2 = round((a1[1] - offa) * sfa, 10)
            x3 = round((a1[2] - offa) * sfa, 10)
            x4 = round((a1[3] - offa) * sfa, 10)
            x5 = round((a1[4] - offa) * sfa, 10)

            y1 = round((o1[0] - offo) * sfo, 8)
            y2 = round((o1[1] - offo) * sfo, 8)
            y3 = round((o1[2] - offo) * sfo, 8)
            y4 = round((o1[3] - offo) * sfo, 8)
            y5 = round((o1[4] - offo) * sfo, 8)

            return x1, x2, x3, x4, x5, y1, y2, y3, y4, y5

        else:

            return 0, 0, 0, 0, 0, 0, 0, 0, 0, 0

    def check_tabel_curve(self, lcss_id):
        if lcss_id in self.dataframe.define_curve:
            return "curve"

        elif lcss_id in self.dataframe.define_table:
            return "table"

        else:
            return None

    def extract_curve_from_table(self, lcss_id):
        current_table = self.dataframe.define_table[lcss_id]

        value = current_table.value
        lcid = current_table.lcid

        sorted_indices = sorted(range(len(value)), key=lambda i: value[i])

        return lcid[sorted_indices[0]] if sorted_indices else None

    def map_material(self, lcss_id):
        lcss_id = abs(lcss_id)    # hard id: -2000 means curve id: 2000 in keywords

        curve_tag = self.check_tabel_curve(lcss_id)
        curve_id = None

        if curve_tag == "curve":
            curve_id = lcss_id
        elif curve_tag == "table":
            curve_id = self.extract_curve_from_table(lcss_id)

        x1, x2, x3, x4, x5, y1, y2, y3, y4, y5 = self.get_curve_info(curve_id=curve_id)

        # print(lcss_id)
        # print(x1, x2, x3, x4, x5)
        # print(y1, y2, y3, y4, y5)

        if x1 == 0 and x2 == 0.0001 and x3 == 0.0002 and x4 == 0.0003 and x5 == 0.0004:
            if y1 == 0.19197 and y2 == 0.20039 and y3 == 0.20303 and y4 == 0.20545 and y5 == 0.20696:
                return "minth_s620"
            elif y1 == 0.134379 and y2 == 0.140273 and y3 == 0.142121 and y4 == 0.143815 and y5 == 0.144872:
                return "minth_s620_haz"

        elif x1 == 0 and x2 == 0.0010000000 and x3 == 0.0020000001 and x4 == 0.0049999999 and x5 == 0.0074999998:
            if y1 == 0.33339999 and y2 == 0.33539999 and y3 == 0.33710001 and y4 == 0.34120001 and y5 == 0.34410001:
                return "minth_s632"
            elif y1 == 0.23337999 and y2 == 0.23477999 and y3 == 0.23597001 and y4 == 0.23884001 and y5 == 0.24087001:
                return "minth_s632_haz"

        elif x1 == 0 and x2 == 0 and x3 == 0 and x4 == 0 and x5 == 0:
            if y1 == 0 and y2 == 0 and y3 == 0 and y4 == 0 and y5 == 0:
                return None

        else:
            return None

    def map_name(self, tag):
        if tag == "minth_s620":
            return "minth_s620"
        elif tag == "minth_s620_haz":
            return "minth_s620_haz"
        elif tag == "minth_s624":
            return "minth_s624"
        elif tag == "minth_s624_haz":
            return "minth_s624_haz"
        elif tag == "minth_s628":
            return "minth_s628"
        elif tag == "minth_s628_haz":
            return "minth_s628_haz"
        elif tag == "minth_s632":
            return "minth_s632"
        elif tag == "minth_s632_haz":
            return "minth_s632_haz"
        elif tag == "minth_s636":
            return "minth_s636"
        elif tag == "minth_s636_haz":
            return "minth_s636_haz"
        else:
            self.num += 1
            return f"default_{self.num}"


material_mapper = MaterialMapper()
