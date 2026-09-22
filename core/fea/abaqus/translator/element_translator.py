from .analysis_data import is_explicit
from core.fea.translator import Translator


class ElementTranslator(Translator):
    def __init__(self):
        super().__init__()

        self.version = {
            "6.14": self._6p14,
        }

    def translate(self, version):
        try:
            if version in self.version:
                self.version[version]()

        except Exception as e:
            raise Exception(f"ABAQUS ElementTranslator ERROR: {e}") from e

    def _6p14(self):
        part_dict = self.dataframe.part
        material_dict = self.dataframe.material
        section_shell_dict = self.dataframe.section_shell
        section_solid_dict = self.dataframe.section_solid

        output_storge = self.dataframe.output_storge

        if len(self.dataframe.storge_part_element) > 0:
            output_storge.setdefault("*ELEMENT", [])

            for pid, element_list in self.dataframe.storge_part_element.items():
                temp_s3 = []
                temp_s4 = []
                temp_tetra4 = []
                temp_pyramid5 = []
                temp_penta6 = []
                temp_hex8 = []

                part_name = part_dict[pid].name
                mid = part_dict[pid].mid
                if mid not in material_dict:
                    raise ValueError(f"Part {pid}: missing material {mid}; check unsupported source material keywords")
                material_name = material_dict[mid].name
                secid = part_dict[pid].secid
                section_name = "default"

                if secid in section_shell_dict:
                    section_name = section_shell_dict[secid].name
                elif secid in section_solid_dict:
                    section_name = section_solid_dict[secid].name

                property_name = section_name + "_" + material_name

                for element in element_list:
                    format = element.format

                    if format == "s3":
                        temp_s3.append(f"{element.uid:<10},"
                                       f"{element.n1:<10},"
                                       f"{element.n2:<10},"
                                       f"{element.n3:<10}\n")

                    elif format == "s4":
                        temp_s4.append(
                            f"{element.uid:<10},"
                            f"{element.n1:<10},"
                            f"{element.n2:<10},"
                            f"{element.n3:<10},"
                            f"{element.n4:<10}\n"
                        )

                    elif format == "tetra4":
                        temp_tetra4.append(
                            f"{element.uid:<10},"
                            f"{element.n1:<10},"
                            f"{element.n2:<10},"
                            f"{element.n3:<10},"
                            f"{element.n4:<10}\n"
                        )

                    elif format == "pyramid5":
                        temp_pyramid5.append(
                            f"{element.uid:<10},"
                            f"{element.n1:<10},"
                            f"{element.n2:<10},"
                            f"{element.n3:<10},"
                            f"{element.n4:<10},"
                            f"{element.n5:<10}\n"
                        )

                    elif format == "penta6":
                        temp_penta6.append(
                            f"{element.uid:<10},"
                            f"{element.n1:<10},"
                            f"{element.n5:<10},"
                            f"{element.n2:<10},"
                            f"{element.n4:<10},"
                            f"{element.n7:<10},"
                            f"{element.n3:<10}\n"
                        )

                    elif format == "hex8":
                        temp_hex8.append(
                            f"{element.uid:<10},"
                            f"{element.n1:<10},"
                            f"{element.n2:<10},"
                            f"{element.n3:<10},"
                            f"{element.n4:<10},"
                            f"{element.n5:<10},"
                            f"{element.n6:<10},"
                            f"{element.n7:<10},"
                            f"{element.n8:<10}\n"
                        )

                if len(temp_s3) > 0:
                    output_storge["*ELEMENT"].append(
                        f"**HW_COMPONENT     ID={pid}     COLOR={pid}     NAME={part_name}     PROPERTY={property_name}\n"
                    )

                    output_storge["*ELEMENT"].append(
                        f"*ELEMENT,TYPE={'S3R' if is_explicit(self.dataframe) else 'S3'},ELSET={property_name}\n"
                    )

                    for line in temp_s3:
                        output_storge["*ELEMENT"].append(line)

                if len(temp_s4) > 0:
                    output_storge["*ELEMENT"].append(
                        f"**HW_COMPONENT     ID={pid}     COLOR={pid}     NAME={part_name}     PROPERTY={property_name}\n"
                    )

                    output_storge["*ELEMENT"].append(
                        f"*ELEMENT,TYPE={'S4R' if is_explicit(self.dataframe) else 'S4'},ELSET={property_name}\n"
                    )

                    for line in temp_s4:
                        output_storge["*ELEMENT"].append(line)

                if len(temp_tetra4) > 0:
                    output_storge["*ELEMENT"].append(
                        f"**HW_COMPONENT     ID={pid}     COLOR={pid}     NAME={part_name}     PROPERTY={property_name}\n"
                    )

                    output_storge["*ELEMENT"].append(
                        f"*ELEMENT,TYPE=C3D4,ELSET={property_name}\n"
                    )

                    for line in temp_tetra4:
                        output_storge["*ELEMENT"].append(line)

                if len(temp_pyramid5) > 0:
                    output_storge["*ELEMENT"].append(
                        f"**HW_COMPONENT     ID={pid}     COLOR={pid}     NAME={part_name}     PROPERTY={property_name}\n"
                    )

                    output_storge["*ELEMENT"].append(
                        f"*ELEMENT,TYPE=C3D5,ELSET={property_name}\n"
                    )

                    for line in temp_pyramid5:
                        output_storge["*ELEMENT"].append(line)

                if len(temp_penta6) > 0:
                    output_storge["*ELEMENT"].append(
                        f"**HW_COMPONENT     ID={pid}     COLOR={pid}     NAME={part_name}     PROPERTY={property_name}\n"
                    )

                    output_storge["*ELEMENT"].append(
                        f"*ELEMENT,TYPE=C3D6,ELSET={property_name}\n"
                    )

                    for line in temp_penta6:
                        output_storge["*ELEMENT"].append(line)

                if len(temp_hex8) > 0:
                    output_storge["*ELEMENT"].append(
                        f"**HW_COMPONENT     ID={pid}     COLOR={pid}     NAME={part_name}     PROPERTY={property_name}\n"
                    )

                    output_storge["*ELEMENT"].append(
                        f"*ELEMENT,TYPE=C3D8,ELSET={property_name}\n"
                    )

                    for line in temp_hex8:
                        output_storge["*ELEMENT"].append(line)









