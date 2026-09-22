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
        }

        self.parse_keywords_2 = {
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

        # Existing geometry/material card layouts are retained for 2023.
        for registry in (self.translate_keywords, self.translate_keywords_mapping):
            for translator in registry.values():
                if hasattr(translator, 'version') and '2020' in translator.version:
                    translator.version['2023'] = translator.version['2020']
            registry.update({
                "GROUP": GroupTranslator(),
                "MTOCO": MtocoTranslator(),
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

        if file_path:
            with open(file=file_path, mode="r", encoding="utf-8", errors="ignore") as f:
                try:
                    for line in f:
                        if (len(line.strip()) == 0) or line.startswith("$") or line.startswith("END"):
                            continue
                        else:
                            pamcrash_keyword = line[0:8].strip()

                            if pamcrash_keyword.endswith("/"):
                                if pamcrash_keyword in parse_keywords:
                                    self.current_parser = parse_keywords[pamcrash_keyword]
                                    self.current_parser.reset()
                                    self.current_parser.parse(line_raw=line, version=version)
                                    continue
                                else:
                                    if pamcrash_keyword in self.parse_keywords_initial:
                                        self.current_parser = None
                                        continue
                                    elif pamcrash_keyword in self.parse_keywords_1:
                                        self.current_parser = None
                                        continue
                                    elif pamcrash_keyword in self.parse_keywords_2:
                                        self.current_parser = None
                                        continue
                                    else:
                                        self.not_support_keywords.add(pamcrash_keyword)
                                        self.current_parser = None
                                        continue
                            elif self.current_parser:
                                self.current_parser.parse(line_raw=line, version=version)

                except Exception as e:
                    raise e

        else:
            self.logger.error(f"file path cannot be empty\n")

    def parse(self, *args, **kwargs):
        file_path = kwargs.get("file_path", args[0] if len(args) > 0 else None)
        version = kwargs.get("version", args[1] if len(args) > 1 else None)

        self.parse_data(file_path=file_path, version=version, parse_keywords=self.parse_keywords_initial)
        self.parse_data(file_path=file_path, version=version, parse_keywords=self.parse_keywords_1)
        self.parse_data(file_path=file_path, version=version, parse_keywords=self.parse_keywords_2)

        for not_support_keyword in self.not_support_keywords:
            self.logger.warning(f"Ls-Dyna not support keywords: {not_support_keyword}")

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

            self.logger.info(f"PAMCRASH translation finished")

        else:
            self.logger.error(f"PAMCRASH TRANSLATOR ERROR: file path cannot be empty\n")
