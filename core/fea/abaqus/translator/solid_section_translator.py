from core.fea.translator import Translator


class SolidSectionTranslator(Translator):
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
            raise Exception(f"ABAQUS NodeTranslator ERROR: {e}") from e

    def _6p14(self):
        part_dict = self.dataframe.part
        material_dict = self.dataframe.material
        section_solid_dict = self.dataframe.section_solid

        if len(part_dict) > 0 and len(section_solid_dict) > 0 and len(material_dict) > 0:
            temp_section_name = set()

            output_storge = self.dataframe.output_storge.setdefault("*SOLID_SECTION", [])

            for pid, part in part_dict.items():
                mid = part_dict[pid].mid
                material_name = material_dict[mid].name
                secid = part_dict[pid].secid

                if secid in section_solid_dict:
                    section_solid = section_solid_dict[secid]

                    section_name = section_solid_dict[secid].name

                    property_name = section_name + "_" + material_name

                    if property_name not in temp_section_name:

                        output_storge.append(f"*SOLID SECTION, "
                                             f"ELSET={property_name}, "
                                             f"MATERIAL={material_name}\n")

                        temp_section_name.add(property_name)




