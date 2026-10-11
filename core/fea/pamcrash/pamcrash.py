from contextlib import nullcontext
from core.fea.include_reader import load_deck, pam_keyword
from core.fea.pamcrash.translator.bounc_translator import BouncTranslator
from core.fea.pamcrash.translator.invel_translator import InvelTranslator
from core.fea.pamcrash.translator.runend_translator import RunendTranslator
from core.fea.pamcrash.parser.group_parser import GroupParser
from core.fea.pamcrash.parser.bounc_parser import BouncParser
from core.fea.pamcrash.parser.invel_parser import InvelParser
from core.fea.pamcrash.parser.runend_parser import RunendParser
from utilities.source_location import source_location, parse_source, source_scope
from core.fea.dataframe import dataframe
from core.fea.mesh_data import rebuild_indices, split_shell_thickness
from core.fea.pamcrash.parser.part_parser import PartParser
from core.fea.validation import FeaInputError, validate_card
from core.fea.pamcrash.translator.group_translator import GroupTranslator
from core.fea.pamcrash.translator.mtoco_translator import MtocoTranslator
from core.fea.pamcrash.translator.thnod_translator import ThnodTranslator
from core.fea.pamcrash.translator.secfo_translator import SecfoTranslator
from core.fea.pamcrash.translator.cntac33_translator import Cntac33Translator
from core.fea.pamcrash.translator.cntac36_translator import Cntac36Translator
from core.fea.pamcrash.translator.cntac43_translator import Cntac43Translator
from utilities.logger import logger
from core.fea.solver import Solver
from core.fea.pamcrash.parser.pyvar_parser import PyvarParser
from core.fea.pamcrash.parser.node_parser import NodeParser
from core.fea.pamcrash.parser.shell_parser import ShellParser
from core.fea.pamcrash.parser.tetr4_parser import Tetr4Parser
from core.fea.pamcrash.parser.solid_parser import SolidParser
from core.fea.pamcrash.parser.secfo_parser import SecFoParser
from core.fea.pamcrash.translator.user_head_note_translator import UserHeadNoteTranslator
from core.fea.pamcrash.translator.node_translator import NodeTranslator
from core.fea.pamcrash.translator.shell_translator import ShellTranslator
from core.fea.pamcrash.translator.solid_translator import SolidTranslator
from core.fea.pamcrash.translator.part_translator import PartTranslator
from core.fea.pamcrash.translator.material_translator import MaterialTranslator
from core.fea.pamcrash.translator.material_mapping_translator import MaterialMappingTranslator
from core.fea.pamcrash.translator.funct_translator import FunctTranslator


class PamCrash(Solver):
    def __init__(self):
        self.logger = logger

        self.parse_keywords_initial = {
            "PYVAR /": PyvarParser(),
        }

        self.parse_keywords_1 = {
            "NODE  /": NodeParser(),
            "SHELL /": ShellParser(),
            "TETR4 /": Tetr4Parser(),
            "SOLID /": SolidParser(),
            "SECFO /": SecFoParser(),
            "PART  /": PartParser(),
            "GROUP /": GroupParser(),
            "RUNEND/": RunendParser(),
        }

        from core.fea.pamcrash.parser.funct_parser import FunctParser
        from core.fea.pamcrash.parser.rbody_parser import RbodyParser
        from core.fea.pamcrash.parser.motion_parser import MotionParser
        from core.fea.pamcrash.parser.mass_parser import MassParser
        self.parse_keywords_1['FUNCT /'] = FunctParser()
        self.parse_keywords_2 = {
            'MASS  /': MassParser(),
            'RBODY /': RbodyParser(),
            'DIS3D /': MotionParser(2), 'VEL3D /': MotionParser(0), 'ACC3D /': MotionParser(1),
            'RAN3D /': MotionParser(2, True), 'RVE3D /': MotionParser(0, True), 'RAC3D /': MotionParser(1, True),
            "BOUNC /": BouncParser(),
            "INVEL /": InvelParser(),
        }

        self.translate_keywords = {
            "note": UserHeadNoteTranslator(),
            "NODE": NodeTranslator(),
            "SHELL": ShellTranslator(),
            "SOLID": SolidTranslator(),
            "PART": PartTranslator(),
            "MATER": MaterialTranslator(),
            "FUNCT": FunctTranslator(),
        }
        self.translate_keywords_mapping = {
            "note": UserHeadNoteTranslator(),
            "NODE": NodeTranslator(),
            "SHELL": ShellTranslator(),
            "SOLID": SolidTranslator(),
            "PART": PartTranslator(),
            "MATER": MaterialMappingTranslator(),
            "FUNCT": FunctTranslator(),
        }

        from core.fea.pamcrash.translator.motion_translator import MotionTranslator
        from core.fea.pamcrash.translator.mass_translator import MassTranslator
        from core.fea.pamcrash.translator.parameter_translator import ParameterTranslator
        from core.fea.pamcrash.translator.control_translator import HeaderTranslator, ControlTranslator
        # Existing geometry/material card layouts are retained for 2023.
        for registry in (self.translate_keywords, self.translate_keywords_mapping):
            # Header records precede the mesh in the resulting native deck.
            registry_items = list(registry.items())
            registry.clear()
            registry.update({'HEADER': HeaderTranslator(), **dict(registry_items)})
            for translator in registry.values():
                if hasattr(translator, 'version') and '2020' in translator.version:
                    translator.version['2023'] = translator.version['2020']
            registry.update({
                "PYVAR": ParameterTranslator(),
                "CONTROL": ControlTranslator(),
                "MASS": MassTranslator(),
                "RUNEND": RunendTranslator(),
                "MTOCO": MtocoTranslator(),
                "MOTION": MotionTranslator(),
                "GROUP": GroupTranslator(),
                "BOUNC": BouncTranslator(),
                "INVEL": InvelTranslator(),
                "THNOD": ThnodTranslator(),
                "SECFO": SecfoTranslator(),
                "CNTAC33": Cntac33Translator(),
                "CNTAC36": Cntac36Translator(),
                "CNTAC43": Cntac43Translator(),
            })

        self.not_support_keywords = set()

        self.current_parser = None

    def reset(self):
        self.current_parser = None
        self.not_support_keywords.clear()

    def parse_data(self, *args, **kwargs):
        file_path = kwargs.get("file_path", args[0] if len(args) > 0 else None)
        version = kwargs.get("version", args[1] if len(args) > 1 else None)
        parse_keywords = kwargs.get("parse_keywords", args[2] if len(args) > 2 else None)

        self.current_parser = None
        active_pam_keyword = None
        encrypted = False
        def finish():
            if self.current_parser and hasattr(self.current_parser, 'finish'):
                with source_scope(self.current_parser.source_context):
                    self.current_parser.finish()
        deck = kwargs.get("deck") or load_deck(file_path, "pamcrash")
        with nullcontext(deck.selected_lines('pamcrash', parse_keywords.__contains__)) as stream:
            try:
                for record in stream:
                    source_path, source_line, line = record.path, record.number, record.text
                    if line.startswith('$'):
                        if active_pam_keyword == 'PART  /' and self.current_parser:
                            self.current_parser.parse(line, version)
                        continue
                    keyword = line[:8].strip()
                    special = pam_keyword(line)
                    if special in ('ACTIVATE_GLOBAL', 'AUTOSLEEP', 'AIRBAGCHECK'):
                        finish()
                        self.current_parser = None
                        if special == 'ACTIVATE_GLOBAL':
                            raise ValueError('ACTIVATE_GLOBAL: modular activation requires scope-aware conversion; flattening it would change the model')
                        self.not_support_keywords.add(source_location(source_path, source_line, special))
                        continue
                    if encrypted:
                        if line.strip().startswith('END_SECURE'):
                            encrypted = False
                        continue
                    if line.strip() == 'ENDDATA' or keyword in ('ANALYSIS', 'TITLE', 'SOLVER', 'UNIT', 'INPUTVER'):
                        finish()
                        self.current_parser = None
                        if line.strip() != 'ENDDATA':
                            self.not_support_keywords.add(source_location(source_path, source_line, keyword))
                        continue
                    if keyword.endswith('/'):
                        finish()
                        active_pam_keyword = keyword
                        if keyword.startswith('SECURE'):
                            encrypted = True
                        self.current_parser = parse_keywords.get(keyword)
                        if self.current_parser:
                            self.current_parser.reset()
                        elif not any(keyword in registry for registry in
                                     (self.parse_keywords_initial, self.parse_keywords_1, self.parse_keywords_2)):
                            if keyword not in ('MATER /', 'FUNCT /'):
                                self.not_support_keywords.add(source_location(source_path, source_line, keyword))
                    elif line.strip().startswith('END_'):
                        finish()
                        self.current_parser = None
                        continue
                    if self.current_parser:
                        # Blank cards are positional, e.g. PART, contacts and materials.
                        if not line.strip() and self.current_parser.__class__.__name__ not in ('PartParser', 'RbodyParser', 'MotionParser', 'FunctParser'):
                            continue
                        parse_source(self.current_parser, line, version, source_path, source_line, active_pam_keyword)
                finish()
            except Exception as error:
                raise FeaInputError(f'{source_location(source_path, locals().get("source_line"), active_pam_keyword)}: {error}') from error

    def parse(self, *args, **kwargs):
        file_path = kwargs.get("file_path", args[0] if len(args) > 0 else None)
        version = kwargs.get("version", args[1] if len(args) > 1 else None)

        from core.fea.material_cards import register_materials
        deck = load_deck(file_path, "pamcrash")
        # Material fields may reference PYVAR assignments from any included file.
        self.parse_data(file_path=file_path, version=version, parse_keywords=self.parse_keywords_initial, deck=deck)
        material_text, material_sources = deck.material_input('pamcrash')
        register_materials(material_text, "pamcrash", file_path=file_path, source_map=material_sources)
        self.parse_data(file_path=file_path, version=version, parse_keywords=self.parse_keywords_1, deck=deck)
        self.parse_data(file_path=file_path, version=version, parse_keywords=self.parse_keywords_2, deck=deck)

        from core.fea.pamcrash.parser.node_selection import nodes
        from core.fea.model.lsdyna.set_node_list import SetNodeList
        for name, group in dataframe.storge['pam_groups'].items():
            try:
                selected = nodes(group.rows, dataframe, (name,))
            except ValueError as error:
                from core.fea.conversion_notes import unconverted
                unconverted(f'GROUP {name}: not converted: {error}', source=group)
                continue
            sid = max(dataframe.set_node_list, default=0)+1
            obj = SetNodeList(uid=sid, name=name)
            obj.ids = selected
            obj.source_context = group.source_context
            dataframe.set_node_list[sid] = obj
        split_shell_thickness(dataframe)
        rebuild_indices(dataframe)

        for not_support_keyword in self.not_support_keywords:
            from core.fea.conversion_notes import unconverted
            unconverted('PAMCRASH keyword is not converted', not_support_keyword)

    def translate(self, *args, **kwargs):
        file_path = kwargs.get("file_path", args[0] if len(args) > 0 else None)
        version = kwargs.get("version", args[1] if len(args) > 1 else None)
        material_mapping = kwargs.get("material_mapping", args[2] if len(args) > 2 else None)
        material_mapping_file_path = kwargs.get("material_mapping_file_path", args[3] if len(args) > 3 else None)

        if file_path:
            if material_mapping:
                for key, translator in self.translate_keywords_mapping.items():
                    self.current_translator = translator

                    if key == "MATER":
                        self.current_translator.translate(version=version,
                                                          material_mapping_file_path=material_mapping_file_path)
                    else:
                        self.current_translator.translate(version=version)
            else:
                for key, translator in self.translate_keywords.items():
                    self.current_translator = translator
                    self.current_translator.translate(version=version)

            from core.fea.pamcrash.translator.tie_translator import TieTranslator
            TieTranslator().translate(version)
            from core.fea.pamcrash.translator.joint_translator import JointTranslator
            JointTranslator().translate(version)
            self.logger.info(f"PAMCRASH translation finished")

        else:
            self.logger.error(f"PAMCRASH TRANSLATOR ERROR: file path cannot be empty\n")
