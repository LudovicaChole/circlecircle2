from utilities.source_location import source_location, parse_source
from core.fea.validation import FeaInputError, validate_card
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
from core.fea.abaqus.translator.nset_translator import NsetTranslator


class Abaqus(Solver):
    def __init__(self):
        self.logger = logger

        self.parse_keywords = {
            "*NODE": NodeParser(),
        }
        self.translate_keywords = {
            "**note": UserHeadNoteTranslator(),
            "*NODE": NodeTranslator(),
            "*NSET": NsetTranslator(),
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
            "*NSET": NsetTranslator(),
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

        from core.fea.abaqus.parser.input_reader import parse_file
        parse_file(file_path, version)

    def translate(self, *args, **kwargs):
        file_path = kwargs.get("file_path", args[0] if len(args) > 0 else None)
        version = kwargs.get("version", args[1] if len(args) > 1 else None)
        material_mapping = kwargs.get("material_mapping", args[2] if len(args) > 2 else None)
        material_mapping_file_path = kwargs.get("material_mapping_file_path", args[3] if len(args) > 3 else None)

        if file_path:
            from core.fea.abaqus.translator.thermal_translator import thermal_mode, translate_thermal
            if thermal_mode(dataframe) == 1:
                translate_thermal(dataframe)
                return
            if thermal_mode(dataframe) == 2:
                from core.fea.abaqus.translator.analysis_data import rigid_dofs
                fixed = bool(dataframe.part) and all(
                    getattr(dataframe.material.get(p.mid), 'tag', None) == 'rigid'
                    and rigid_dofs(dataframe.material[p.mid]) == {1, 2, 3, 4, 5, 6}
                    for p in dataframe.part.values())
                moving = (dataframe.initial_velocity_generation or dataframe.boundary_prescribed_motion_rigid
                          or dataframe.storge['initial_velocity_node'] or dataframe.storge['electromagnetic'])
                if not fixed or moving:
                    raise ValueError('Coupled thermal-structural analysis is not yet mapped to Abaqus; '
                                     'it cannot be replaced with an uncoupled heat-transfer step')
                from core.fea.conversion_notes import unconverted
                unconverted('Combined analysis reduced to heat transfer because every part is a fully fixed rigid body')
                translate_thermal(dataframe)
                return
            if dataframe.storge['thermal']:
                from core.fea.conversion_notes import unconverted
                for record in dataframe.storge['thermal'].values():
                    unconverted(f'{record.keyword}: thermal card has no active thermal analysis mapping '
                                'in this structural conversion', record)
            from core.fea.abaqus.translator.names import material_names
            material_names(dataframe)
            from core.fea.mesh_cleanup import remove_duplicate_solids
            remove_duplicate_solids(dataframe)
            from core.fea.abaqus.translator.beam_translator import BeamTranslator
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

            from core.fea.hourglass_notes import write_comments
            dataframe.output_storge['**HOURGLASS_NOTES'] = write_comments(dataframe)
            BeamTranslator().translate(version)
            from core.fea.abaqus.translator.joint_translator import JointTranslator
            JointTranslator().translate(version)
            notices = []
            for key in ('mat_add_damage_gissmo', 'contact_single_edge_id'):
                if dataframe.storge.get(key):
                    notice = f'{key}: parsed source data retained, but no equivalent Abaqus conversion implemented'
                    for record in dataframe.storge[key].values():
                        self.logger.warning(notice, source=record)
                    notices.append('** CONVERSION LIMITATION: ' + notice + '\n')
            if notices:
                dataframe.output_storge['**LIMITATIONS'] = notices
            self.logger.info(f"ABAQUS translation finished")

        else:
            self.logger.error(f"ABAQUS TRANSLATOR ERROR: file path cannot be empty\n")
