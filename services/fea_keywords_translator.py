import os
from utilities.logger import logger
from core.fea.dataframe import dataframe
from core.fea.lsdyna.lsdyna import LsDyna
from core.fea.abaqus.abaqus import Abaqus
from core.fea.abaqus.translator.step_translator import StepTranslator
from core.fea.pamcrash.pamcrash import PamCrash


class FeaKeywordsTranslator:
    def __init__(self):
        self.logger = logger

        self.dataframe = dataframe

        self.work_folder = None
        self.current_file_name = None

    def reset(self):
        self.dataframe.reset()

    def translate(self, *args, **kwargs):
        """
        :param file_path: target file full path
        :param solver1: parser solver
        :param version1:
        :param solver2: translate solver
        :param version2:
        :param material_mapping: use matching target-solver material templates when True
        :param material_mapping_file_path: JSON file or directory containing material_mapping.json
        :return:
        """
        self.reset()

        file_path = kwargs.get("file_path", args[0] if len(args) > 0 else None)
        solver1 = kwargs.get("solver1", args[1] if len(args) > 1 else None)
        version1 = kwargs.get("version1", args[2] if len(args) > 2 else None)
        solver2 = kwargs.get("solver2", args[3] if len(args) > 3 else None)
        version2 = kwargs.get("version2", args[4] if len(args) > 4 else None)
        material_mapping = kwargs.get("material_mapping", args[5] if len(args) > 5 else None)
        material_mapping_file_path = kwargs.get("material_mapping_file_path", args[6] if len(args) > 6 else None)
        solver1 = self.normalize_solver(solver1)
        solver2 = self.normalize_solver(solver2)

        if not file_path or not os.path.isfile(file_path):
            raise ValueError(f'Source file does not exist: {file_path}')
        supported = {'lsdyna': {'12.0','13.0'}, 'abaqus': {'6.14'}, 'pamcrash': {'2020'}}
        targets = {'lsdyna': set(), 'abaqus': {'6.14'}, 'pamcrash': {'2020','2023'}}
        if solver1 not in supported or version1 not in supported[solver1]:
            raise ValueError(f'Unsupported source solver/version: {solver1} {version1}')
        if solver2 != 'parse_only' and (solver2 not in targets or version2 not in targets[solver2]):
            raise ValueError(f'Unsupported target solver/version: {solver2} {version2}')
        if solver1 == solver2:
            raise ValueError('Source and target solvers must be different')

        folder, basename, file_name, file_extension = self.disassemble_file_path(file_path=file_path)
        self.work_folder = folder
        self.current_file_name = file_name

        if solver1 == solver2:
            self.logger.error(f"FEA KEYWORDS TRANSLATOR ERROR: "
                              f"solver1 {solver1} and solver2 {solver2} must be different\n")

        else:
            if solver1 == "lsdyna":
                if version1 in ["12.0", "13.0"] and (file_extension.lower() == ".k" or file_extension.lower() == ".key"):
                    self._lsdyna(version=version1,
                                 file_path=file_path,
                                 mode="parse",
                                 material_mapping=material_mapping,
                                 material_mapping_file_path=material_mapping_file_path)
                else:
                    self.logger.error(f"FEA KEYWORDS TRANSLATOR ERROR: "
                                      f"current ls-dyna version {version1} or extension {file_extension} not supported\n")

            elif solver1 == "abaqus":
                if version1 in ["6.14"] and (file_extension.lower() == ".inp" or file_extension.lower() == ".geo"):
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

            if solver2 == "lsdyna":
                if version2 in ["12.0", "13.0"]:
                    self._lsdyna(version=version2,
                                 file_path=file_path,
                                 mode="translate",
                                 material_mapping=material_mapping,
                                 material_mapping_file_path=material_mapping_file_path)
                else:
                    self.logger.error(f"FEA KEYWORDS TRANSLATOR ERROR: "
                                      f"current ls-dyna version {version2} not supported\n")

            elif solver2 == "abaqus":
                if version2 in ["6.14"]:
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
            self.logger.debug(f"lsdyna translate mode, version: {version}, file_path: {file_path}")

    def _abaqus(self, version, file_path, mode, material_mapping, material_mapping_file_path):
        abaqus = Abaqus()

        if mode == "parse":
            abaqus.parse(file_path=file_path, version=version)

        elif mode == "translate":
            abaqus.translate(file_path=file_path,
                             version=version,
                             material_mapping=material_mapping,
                             material_mapping_file_path=material_mapping_file_path)

            folder, basename, file_name, file_extension = self.disassemble_file_path(file_path=file_path)

            model_path = os.path.join(folder, file_name + "_test.geo")
            # Validate all step data before writing either of the two deliverables.
            step_lines = StepTranslator().translate(version=version)
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
        with open(step_path, mode="w", encoding="utf-8") as f:
            f.write(f'*INCLUDE, INPUT="{os.path.basename(model_file_path)}"\n')
            f.writelines(lines)
        self.logger.info(f"Analysis launch file generated: {step_path}")
        return step_path

    def write_file(self, file_path):
        if len(self.dataframe.output_storge) > 0:
            with open(file_path, mode="w", encoding="utf-8", errors="ignore") as f:
                for keyword, content in self.dataframe.output_storge.items():
                    if keyword == "*STEP_CONTACT":
                        continue
                    for line in content:
                        f.write(line)

            self.logger.info(f"All Done\n")

        else:
            self.logger.warning(f"FEA KEYWORDS TRANSLATOR WARNING: no data need to translate\n")

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
    file_path = r"C:\Users\jiand\PycharmProjects\circlecircle2\Test_Items\data3.k"
    material_mapping_file_path = r"C:\Users\jiand\PycharmProjects\circlecircle2\Test_Items\material_mapping.json"
    # file_path = r"C:\Users\jiand\Downloads\Test_Data\test_model.inp"
    # file_path = r"C:\Users\jiand\Downloads\Test_Data\test_.pc"

    fea_keywords_translator.translate(file_path=file_path,
                                      solver1="lsdyna",
                                      version1="12.0",
                                      solver2="abaqus",
                                      version2="6.14",
                                      material_mapping=True,
                                      material_mapping_file_path=material_mapping_file_path)
#
#     d = fea_keywords_translator.dataframe
    # print(d.define_curve)
    # print(d.define_table)
    # print(d.storge_part)

    # for k, v in d.storge_part_node.items():
    #     print(f"pid is {k}, length is {len(v)}")
    #     # if v.map_tag == "minth_s620_haz":
    #     #     print(f"mid is {k}")
    #     #     print(v)


