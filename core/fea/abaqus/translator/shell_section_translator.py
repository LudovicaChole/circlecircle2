from core.fea.translator import Translator


class ShellSectionTranslator(Translator):
    def __init__(self):
        super().__init__()

        self.version = {
            "6.14": self._6p14, "2024": self._6p14,
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
        section_shell_dict = self.dataframe.section_shell

        if len(part_dict) > 0 and len(section_shell_dict) > 0 and len(material_dict) > 0:
            temp_section_name = set()

            output_storge = self.dataframe.output_storge.setdefault("*SHELL_SECTION", [])

            for pid, part in part_dict.items():
                if not self.dataframe.storge_part_element.get(pid):
                    continue
                mid = part_dict[pid].mid
                material_name = material_dict[mid].name
                secid = part_dict[pid].secid

                if secid in section_shell_dict:
                    section_shell = section_shell_dict[secid]

                    section_name = section_shell_dict[secid].name

                    property_name = section_name + "_" + material_name

                    if property_name not in temp_section_name:

                        t1 = section_shell.t1
                        nip = section_shell.nip or 2
                        if float(nip).is_integer() and 2 <= nip <= 10:
                            integration = ', SECTION INTEGRATION=GAUSS'
                            nip = int(nip)
                        else:
                            from core.fea.conversion_notes import unconverted
                            unconverted(
                                f'Shell section {secid}: NIP={section_shell.nip:g} has no mapped '
                                'Abaqus integration rule; using 5-point Simpson integration', section_shell)
                            integration, nip = '', 5

                        output_storge.append(f"*SHELL SECTION, "
                                             f"ELSET={property_name}, "
                                             f"MATERIAL={material_name}{integration}\n")

                        output_storge.append(f"{t1:<10},{nip:<10}\n")

                        temp_section_name.add(property_name)


