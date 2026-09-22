from utilities.logger import logger
from core.fea.translator import Translator


class MaterialTranslator(Translator):
    def __init__(self):
        super().__init__()

        self.version = {
            "6.14": self._6p14,
        }

    def translate(self, version, material_mapping=None):
        try:
            if version in self.version:
                self.version[version](material_mapping)

        except Exception as e:
            raise Exception(f"ABAQUS NodeTranslator ERROR: {e}") from e

    def _6p14(self, material_mapping=None):
        if len(self.dataframe.material) > 0:
            part_dict = self.dataframe.part
            material_dict = self.dataframe.material
            curve_dict = self.dataframe.define_curve
            table_dict = self.dataframe.define_table

            output_storge = self.dataframe.output_storge.setdefault("*MATERIAL", [])

            temp_material_set = set()

            for pid, part in part_dict.items():
                mid = part.mid

                material = material_dict[mid]

                material_name = material.name

                rho = material.rho

                e = material.e

                pr = material.pr

                material_tag = material.tag

                if mid in temp_material_set:
                    continue
                else:
                    temp_material_set.add(mid)

                    if material_mapping is not None:
                        mapped_material = material_mapping.render(material, mid)
                        if mapped_material is not None:
                            output_storge.append(mapped_material)
                            continue

                    if material_tag == "elastic" or material_tag == "rigid":
                        output_storge.append(
                            f"*MATERIAL, NAME={material_name}\n"
                            f"*DENSITY\n"
                            f"{rho}, 0.0\n"
                            f"*ELASTIC, TYPE = ISOTROPIC\n"
                            f"{e}, {pr}, 0.0\n"
                        )

                    elif material_tag == "plastic":
                        output_storge.append(
                            f"*MATERIAL, NAME={material_name}\n"
                            f"*DENSITY\n"
                            f"{rho}, 0.0\n"
                            f"*ELASTIC, TYPE = ISOTROPIC\n"
                            f"{e}, {pr}, 0.0\n"
                        )

                        lcss = abs(material.lcss)

                        curve_type = self.check_tabel_curve(lcss_id=lcss,
                                                            curve_dict=curve_dict,
                                                            table_dict=table_dict)

                        if curve_type == "curve":
                            self.combine_curve_data(lcss_id=lcss,
                                                    curve_dict=curve_dict,
                                                    output_storge=output_storge)
                        elif curve_type == "table":
                            lcid = self.extract_curve_from_table(lcss_id=lcss,
                                                                 table_dict=table_dict)

                            self.combine_curve_data(lcss_id=lcid,
                                                    curve_dict=curve_dict,
                                                    output_storge=output_storge)
                        else:
                            if lcss:
                                raise ValueError(f'Material {mid}: missing stress/strain curve or table {lcss}')
                            points = [(getattr(material, f'eps{i}', 0), getattr(material, f'es{i}', 0)) for i in range(1,9)]
                            points = [(strain, stress) for strain, stress in points if stress > 0]
                            if not points:
                                yield_stress = getattr(material, 'sigy', 0)
                                tangent = getattr(material, 'etan', 0)
                                if yield_stress <= 0:
                                    raise ValueError(f'Material {mid}: no positive yield stress or plastic curve')
                                points = [(0.0, yield_stress)]
                                if tangent:
                                    if tangent < 0 or tangent >= e:
                                        raise ValueError(f'Material {mid}: ETAN must satisfy 0 <= ETAN < E')
                                    points.append((1.0, yield_stress + e*tangent/(e-tangent)))
                            if points[0][0] != 0 or any(b[0] <= a[0] for a,b in zip(points,points[1:])):
                                raise ValueError(f'Material {mid}: plastic strain must start at zero and strictly increase')
                            output_storge.append('*PLASTIC\n')
                            output_storge.extend(f'{stress}, {strain}\n' for strain,stress in points)

    def combine_curve_data(self, lcss_id, curve_dict, output_storge):
        curve = curve_dict[lcss_id]

        sfa = curve.sfa
        sfo = curve.sfo
        offa = curve.offa
        offo = curve.offo

        output_storge.append("*PLASTIC\n")

        for item_index in range(len(curve.a1)):
            a1 = (curve.a1[item_index] + offa) * sfa
            o1 = (curve.o1[item_index] + offo) * sfo

            output_storge.append(f"{o1:<20},{a1:<20}\n")

    def check_tabel_curve(self, lcss_id, curve_dict, table_dict):
        if lcss_id in curve_dict:
            return "curve"

        elif lcss_id in table_dict:
            return "table"

        else:
            return None

    def extract_curve_from_table(self, lcss_id, table_dict):
        current_table = table_dict[lcss_id]

        value = current_table.value
        lcid = current_table.lcid

        sorted_indices = sorted(range(len(value)), key=lambda i: value[i])

        return lcid[sorted_indices[0]]