from core.fea.dataframe import dataframe
from core.fea.abaqus.translator.initial_state_translator import InitialStateTranslator
from utilities.logger import logger
from core.fea.abaqus.translator.history_node_translator import HistoryNodeTranslator
from core.fea.abaqus.translator.contact_pair_translator import ContactPairTranslator
from core.fea.solver import Solver
from core.fea.abaqus.parser.node_parser import NodeParser
from core.fea.abaqus.translator.user_head_note_translator import UserHeadNoteTranslator
from core.fea.abaqus.translator.node_translator import NodeTranslator
from core.fea.abaqus.translator.element_translator import ElementTranslator
from core.fea.abaqus.translator.material_translator import MaterialTranslator
from core.fea.abaqus.translator.material_mapping_translator import MaterialMappingTranslator
from core.fea.abaqus.translator.shell_section_translator import ShellSectionTranslator
from core.fea.abaqus.translator.solid_section_translator import SolidSectionTranslator
from core.fea.abaqus.translator.kinematic_coupling_translator import KinematicCouplingTranslator
from core.fea.abaqus.translator.boundary_translator import BoundaryTranslator


class Abaqus(Solver):
    def __init__(self):
        self.logger = logger

        self.parse_keywords = {
            "*NODE": NodeParser(),
        }
        self.translate_keywords = {
            "**note": UserHeadNoteTranslator(),
            "*NODE": NodeTranslator(),
            "*ELEMENT": ElementTranslator(),
            "*MATERIAL": MaterialTranslator(),
            "*SHELL_SECTION": ShellSectionTranslator(),
            "*SOLID_SECTION": SolidSectionTranslator(),
            "*KINEMATIC_COUPLING": KinematicCouplingTranslator(),
            "*CONTACT PAIR": ContactPairTranslator(),
            "*BOUNDARY": BoundaryTranslator(),
            "*HISTORY_NODE": HistoryNodeTranslator(),
            "*INITIAL_STATE": InitialStateTranslator(),
        }

        self.translate_keywords_mapping = {
            "**note": UserHeadNoteTranslator(),
            "*NODE": NodeTranslator(),
            "*ELEMENT": ElementTranslator(),
            "*MATERIAL": MaterialMappingTranslator(),
            "*SHELL_SECTION": ShellSectionTranslator(),
            "*SOLID_SECTION": SolidSectionTranslator(),
            "*KINEMATIC_COUPLING": KinematicCouplingTranslator(),
            "*CONTACT PAIR": ContactPairTranslator(),
            "*BOUNDARY": BoundaryTranslator(),
            "*HISTORY_NODE": HistoryNodeTranslator(),
            "*INITIAL_STATE": InitialStateTranslator(),
        }

        self.not_support_keywords = set()

        self.current_parser = None
        self.current_translator = None

    def reset(self):
        self.not_support_keywords.clear()

        self.current_parser = None
        self.current_translator = None

    def parse(self, *args, **kwargs):
        file_path = kwargs.get("file_path", args[0] if len(args) > 0 else None)
        version = kwargs.get("version", args[1] if len(args) > 1 else None)

        if file_path:
            with open(file=file_path, mode="r", encoding="utf-8", errors="ignore") as f:
                try:
                    for line in f:
                        if not line or line.startswith("**"):
                            continue

                        if line.startswith("*") and (not line.startswith("**")):
                            abaqus_keyword = line.split(",")[0].strip().upper()

                            if abaqus_keyword in self.parse_keywords:
                                self.current_parser = self.parse_keywords[abaqus_keyword]
                                continue
                            else:
                                self.not_support_keywords.add(abaqus_keyword)
                                self.current_parser = None
                                continue
                        else:
                            if self.current_parser:
                                self.current_parser.parse(line_raw=line, version=version)

                except Exception as e:
                    raise e

            for not_support_keyword in self.not_support_keywords:
                self.logger.warning(f"ABAQUS WARNING: not support keyword: {not_support_keyword}")

        else:
            self.logger.error(f"ABAQUS PARSER ERROR: file path cannot be empty\n")

    def translate(self, *args, **kwargs):
        file_path = kwargs.get("file_path", args[0] if len(args) > 0 else None)
        version = kwargs.get("version", args[1] if len(args) > 1 else None)
        material_mapping = kwargs.get("material_mapping", args[2] if len(args) > 2 else None)
        material_mapping_file_path = kwargs.get("material_mapping_file_path", args[3] if len(args) > 3 else None)

        if file_path:
            if material_mapping:
                for key, translator in self.translate_keywords_mapping.items():
                    self.current_translator = translator

                    if key == "*MATERIAL":
                        self.current_translator.translate(version=version,
                                                          material_mapping_file_path=material_mapping_file_path)
                    else:
                        self.current_translator.translate(version=version)
            else:
                for key, translator in self.translate_keywords.items():
                    self.current_translator = translator
                    self.current_translator.translate(version=version)

            notices = []
            for key in ('mat_add_damage_gissmo', 'contact_single_edge_id', 'contact_automatic_single_surface_id'):
                if dataframe.storge.get(key):
                    notice = f'{key}: parsed source data retained, but no equivalent Abaqus conversion implemented'
                    self.logger.warning(notice)
                    notices.append('** CONVERSION LIMITATION: ' + notice + '\n')
            if notices:
                dataframe.output_storge['**LIMITATIONS'] = notices
            self.logger.info(f"ABAQUS translation finished")

        else:
            self.logger.error(f"ABAQUS TRANSLATOR ERROR: file path cannot be empty\n")
