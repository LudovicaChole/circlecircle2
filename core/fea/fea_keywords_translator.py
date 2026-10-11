import sys
from pathlib import Path
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import os
from utilities.logger import logger
from utilities.source_location import source_location, source_scope
from core.fea.dataframe import dataframe
from core.fea.lsdyna.lsdyna import LsDyna
from core.fea.abaqus.abaqus import Abaqus
from core.fea.abaqus.translator.step_translator import StepTranslator
from core.fea.pamcrash.pamcrash import PamCrash
from core.fea.conversion_support import development_warning, TranslationUnderDevelopment


class FeaKeywordsTranslator:
    def __init__(self):
        self.logger = logger

        self.dataframe = dataframe

        self.work_folder = None
        self.current_file_name = None

    def reset(self):
        self.dataframe.reset()

    def translate(self, *args, **kwargs):
        try:
            path = kwargs.get('file_path', args[0] if args else None)
            with source_scope(source_location(path)):
                return self._translate(*args, **kwargs)
        except Exception as error:
            # Writers are not invoked until parsing and validation succeed.
            self.dataframe.output_storge.clear()
            self.dataframe.output_history_node.clear()
            if not getattr(error, 'fea_logged', False):
                self.logger.error(f'FEA conversion stopped: {error}', source=source_location(path))
                error.fea_logged = True
            raise

    def _translate(self, *args, **kwargs):
        """
        :param file_path: target file full path
        :param solver1: parser solver
        :param version1:
        :param solver2: translate solver
        :param version2:
        :param material_mapping: use matching target-solver material templates when True
        :param material_mapping_file_path: Material directory containing solver subfolders
        :return:
        """
        self.reset()
        self.archive_sources = {}
        self.archive_deck = None

        self.towing_options = kwargs.get('towing_options')
        self.auto_towing = False

        file_path = kwargs.get("file_path", args[0] if len(args) > 0 else None)
        solver1 = kwargs.get("solver1", args[1] if len(args) > 1 else None)
        version1 = kwargs.get("version1", args[2] if len(args) > 2 else None)
        solver2 = kwargs.get("solver2", args[3] if len(args) > 3 else None)
        self.auto_towing = (self.normalize_solver(solver1) == 'lsdyna' and
                            self.normalize_solver(solver2) == 'abaqus')
        version2 = kwargs.get("version2", args[4] if len(args) > 4 else None)
        material_mapping = kwargs.get("material_mapping", args[5] if len(args) > 5 else True)
        material_mapping_file_path = kwargs.get("material_mapping_file_path", args[6] if len(args) > 6 else None)
        solver1 = self.normalize_solver(solver1)
        solver2 = self.normalize_solver(solver2)

        file_path = os.path.normpath(os.path.abspath(file_path)) if file_path else file_path
        if not file_path or not os.path.isfile(file_path):
            raise ValueError(f'Source file does not exist: {file_path}')
        supported = {'lsdyna': {'12.0','13.0','16.0'}, 'abaqus': {'6.14','2024'}, 'pamcrash': {'2020'}}
        targets = {'lsdyna': {'12.0', '13.0', '16.0'}, 'abaqus': {'6.14','2024'}, 'pamcrash': {'2020','2023'}}
        if solver1 not in supported or version1 not in supported[solver1]:
            raise ValueError(f'Unsupported source solver/version: {solver1} {version1}')
        if solver2 != 'parse_only' and (solver2 not in targets or version2 not in targets[solver2]):
            raise ValueError(f'Unsupported target solver/version: {solver2} {version2}')
        if solver1 == solver2:
            raise ValueError('Source and target solvers must be different')

        warning = development_warning(solver1, solver2, version2)
        if warning:
            self.logger.warning(warning)
            error = TranslationUnderDevelopment(warning)
            error.fea_logged = True
            raise error

        from core.fea.include_reader import load_deck
        from core.fea.roundtrip_archive import split_archive
        self.archive_deck = load_deck(file_path, solver1)
        clean, archived, unchanged = split_archive(self.archive_deck.text)
        self.archive_sources = archived
        self.archive_sources[solver1] = clean
        if solver2 in archived and unchanged:
            restored = archived[solver2]
            self.write_restored(file_path, solver2, restored)
            self.logger.info(f'Restored archived {solver2} source deck (includes expanded).')
            return
        if archived and not unchanged:
            self.logger.warning('Generated deck was edited; converting current data instead of restoring an older source.')

        if solver1 == 'lsdyna' and solver2 == 'pamcrash':
            from core.fea.include_reader import load_deck
            from core.fea.pamcrash.translator.conversion_limits import check_dyna_mapping
            check_dyna_mapping(load_deck(file_path, 'lsdyna'))
        if solver1 == 'lsdyna' and solver2 == 'abaqus':
            from core.fea.include_reader import load_deck
            from core.fea.abaqus.translator.conversion_limits import check_dyna_fluid_mapping
            check_dyna_fluid_mapping(load_deck(file_path, 'lsdyna'))


        folder, basename, file_name, file_extension = self.disassemble_file_path(file_path=file_path)
        self.work_folder = folder
        self.current_file_name = file_name

        if solver1 == solver2:
            self.logger.error(f"FEA KEYWORDS TRANSLATOR ERROR: "
                              f"solver1 {solver1} and solver2 {solver2} must be different\n")

        else:
            if solver1 == "lsdyna":
                if version1 in ["12.0", "13.0", "16.0"] and (file_extension.lower() == ".k" or file_extension.lower() == ".key"):
                    self._lsdyna(version=version1,
                                 file_path=file_path,
                                 mode="parse",
                                 material_mapping=material_mapping,
                                 material_mapping_file_path=material_mapping_file_path)
                else:
                    self.logger.error(f"FEA KEYWORDS TRANSLATOR ERROR: "
                                      f"current ls-dyna version {version1} or extension {file_extension} not supported\n")

            elif solver1 == "abaqus":
                if version1 in ["6.14", "2024"] and (file_extension.lower() == ".inp" or file_extension.lower() == ".geo"):
                    self._abaqus(version=version1,
                                 file_path=file_path,
                                 mode="parse",
                                 material_mapping=material_mapping,
                                 material_mapping_file_path=material_mapping_file_path)
                else:
                    self.logger.error(f"FEA KEYWORDS TRANSLATOR ERROR: "
                                      f"current abaqus version {version1} or extension {file_extension} not supported\n")

            elif solver1 == "pamcrash":
                if version1 in ["2020"] and (file_extension.lower() == ".pc" or file_extension.lower() == ".inc"):
                    self._pamcrash(version=version1,
                                   file_path=file_path,
                                   mode="parse",
                                   material_mapping=material_mapping,
                                   material_mapping_file_path=material_mapping_file_path)
                else:
                    self.logger.error(f"FEA KEYWORDS TRANSLATOR ERROR: "
                                      f"current pamcrash version {version1} or extension {file_extension} not supported\n")

            from core.fea.hourglass_notes import capture, restore
            capture(self.dataframe, clean, solver1)
            if solver1 == 'abaqus':
                restore(self.dataframe, clean, solver2)

            if solver2 != 'parse_only':
                from core.fea.lsdyna.translator.rigid_couplings import prepare
                prepare(self.dataframe, solver2)
                from core.fea.validation import validate_references
                validate_references(self.dataframe)

            if solver2 == "lsdyna":
                if version2 in ["12.0", "13.0", "16.0"]:
                    self._lsdyna(version=version2,
                                 file_path=file_path,
                                 mode="translate",
                                 material_mapping=material_mapping,
                                 material_mapping_file_path=material_mapping_file_path)
                else:
                    self.logger.error(f"FEA KEYWORDS TRANSLATOR ERROR: "
                                      f"current ls-dyna version {version2} not supported\n")

            elif solver2 == "abaqus":
                if version2 in ["6.14", "2024"]:
                    self._abaqus(version=version2,
                                 file_path=file_path,
                                 mode="translate",
                                 material_mapping=material_mapping,
                                 material_mapping_file_path=material_mapping_file_path)
                else:
                    self.logger.error(f"FEA KEYWORDS TRANSLATOR ERROR: "
                                      f"current abaqus version {version2} not supported\n")

            elif solver2 == "pamcrash":
                if version2 in ["2020", "2023"]:
                    self._pamcrash(version=version2,
                                   file_path=file_path,
                                   mode="translate",
                                   material_mapping=material_mapping,
                                   material_mapping_file_path=material_mapping_file_path)
                else:
                    self.logger.error(f"FEA KEYWORDS TRANSLATOR ERROR: "
                                      f"current pamcrash version {version2} not supported\n")

            elif solver2 == "parse_only":
                self.logger.info(f"only parse fea file and do not translate any keywords\n")

    def _lsdyna(self, version, file_path, mode, material_mapping, material_mapping_file_path):
        lsdyna = LsDyna()

        if mode == "parse":
            lsdyna.parse(file_path=file_path, version=version)

        elif mode == "translate":
            lsdyna.translate(file_path, version, material_mapping, material_mapping_file_path)
            folder, _, name, _ = self.disassemble_file_path(file_path)
            self.write_file(os.path.join(folder, name + '_test.k'))

    def _abaqus(self, version, file_path, mode, material_mapping, material_mapping_file_path):
        abaqus = Abaqus()

        if mode == "parse":
            abaqus.parse(file_path=file_path, version=version)

        elif mode == "translate":
            abaqus.translate(file_path=file_path,
                             version=version,
                             material_mapping=material_mapping,
                             material_mapping_file_path=material_mapping_file_path)

            if self.auto_towing:
                from core.hmdesktop.towing_conversion import append_towing
                append_towing(self.dataframe, self.towing_options)

            folder, basename, file_name, file_extension = self.disassemble_file_path(file_path=file_path)

            model_path = os.path.join(folder, file_name + "_test.geo")
            # Validate all step data before writing either of the two deliverables.
            step_lines = StepTranslator().translate(version=version) if self.dataframe.part else []
            self.write_file(file_path=model_path)
            self.write_step_file(model_file_path=model_path, version=version, lines=step_lines)

    def _pamcrash(self, version, file_path, mode, material_mapping, material_mapping_file_path):
        pamcrash = PamCrash()

        if mode == "parse":
            pamcrash.parse(file_path=file_path, version=version)

        elif mode == "translate":
            pamcrash.translate(file_path=file_path,
                               version=version,
                               material_mapping=material_mapping,
                               material_mapping_file_path=material_mapping_file_path)

            from core.fea.conversion_notes import unconverted
            for load in self.dataframe.storge['load_node'].values():
                unconverted('Cannot convert nodal load to PAM-CRASH: CONLO mapping is not verified', load)
            for eigen in self.dataframe.storge['implicit_eigenvalue'].values():
                unconverted('Cannot convert eigenvalue analysis to PAM-CRASH: analysis mapping is not verified', eigen)

            folder, basename, file_name, file_extension = self.disassemble_file_path(file_path=file_path)

            new_file_path = os.path.join(folder, file_name + "_test.inc")

            self.write_file(file_path=new_file_path)

    def write_step_file(self, model_file_path, version, lines=None):
        folder = os.path.dirname(model_file_path)
        stem = os.path.splitext(os.path.basename(model_file_path))[0]
        step_path = os.path.join(folder, stem + ".inp")
        if os.path.abspath(step_path) == os.path.abspath(model_file_path):
            raise ValueError("Model filename must use .geo, distinct from the launch .inp")
        if lines is None:
            lines = StepTranslator().translate(version=version)
        from core.fea.roundtrip_archive import comments, split_archive
        with open(model_file_path, encoding='utf-8') as model:
            model_body, _, _ = split_archive(model.read())
        step_body = ''.join(lines)
        with open(step_path, mode="w", encoding="utf-8") as f:
            f.write(f'*INCLUDE, INPUT="{os.path.basename(model_file_path)}"\n')
            f.write(step_body)
            f.write(comments(model_body + step_body, self.archive_sources, 'abaqus'))
        self.logger.info(f"Analysis launch file generated: {step_path}")
        return step_path

    def write_file(self, file_path):
        if len(self.dataframe.output_storge) > 0:
            prefix = '**' if str(file_path).lower().endswith(('.geo', '.inp')) else '$'
            body = ''.join(line for keyword, content in self.dataframe.output_storge.items()
                           if keyword not in ('*STEP_CONTACT', '*THERMAL_STEP') for line in content)
            if body and not body.endswith('\n'):
                body += '\n'
            for note in self.dataframe.storge['conversion_notes']:
                body += f'{prefix} NOT CONVERTED: {note}\n'
            from core.fea.roundtrip_archive import comments
            solver = 'abaqus' if prefix == '**' else ('lsdyna' if str(file_path).lower().endswith(('.k', '.key')) else 'pamcrash')
            with open(file_path, 'w', encoding='utf-8') as stream:
                stream.write(body)
                stream.write(comments(body, self.archive_sources, solver))

            if self.dataframe.storge['conversion_notes']:
                count = len(self.dataframe.storge['conversion_notes'])
                self.logger.warning(
                    f'Partial conversion: {count} unmapped source features. '
                    f'See NOT CONVERTED comments in {file_path} and the warnings above.')
            else:
                self.logger.info(f"All Done\n")

        else:
            self.logger.warning(f"FEA KEYWORDS TRANSLATOR WARNING: no data need to translate\n")

    def write_restored(self, source_path, solver, text):
        from core.fea.roundtrip_archive import comments
        folder, _, stem, _ = self.disassemble_file_path(source_path)
        suffix = {'lsdyna': '.k', 'abaqus': '.geo', 'pamcrash': '.inc'}[solver]
        target = os.path.join(folder, stem + '_test' + suffix)
        if text and not text.endswith('\n'):
            text += '\n'
        with open(target, 'w', encoding='utf-8') as stream:
            stream.write(text)
            stream.write(comments(text, self.archive_sources, solver))
        if solver == 'abaqus':
            launch = os.path.splitext(target)[0] + '.inp'
            with open(launch, 'w', encoding='utf-8') as stream:
                stream.write(f'*INCLUDE, INPUT="{os.path.basename(target)}"\n')

    @staticmethod
    def normalize_solver(solver):
        return str(solver).strip().lower().replace("-", "").replace(" ", "")

    def disassemble_file_path(self, file_path):
        folder = os.path.dirname(file_path)
        basename = os.path.basename(file_path)
        file_name, file_extension = os.path.splitext(basename)

        return folder, basename, file_name, file_extension


fea_keywords_translator = FeaKeywordsTranslator()


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[2]
    file_path = str(root / 'test' / 'data3_empty.k')
    from utilities.profile_settings import ProfileSettings
    logger.configure_profile(ProfileSettings())
    try:
        fea_keywords_translator.translate(file_path=file_path, solver1='lsdyna', version1='12.0',
            solver2='abaqus', version2='6.14', material_mapping=True,
            material_mapping_file_path=None)
    except (ValueError, OSError):
        raise SystemExit(1) from None
