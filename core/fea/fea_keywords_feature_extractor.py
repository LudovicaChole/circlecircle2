"""Extract FEA part features through the shared solver conversion API."""
from utilities.logger import logger
from core.fea.fea_keywords_translator import fea_keywords_translator
from core.fea.tbox import tbox
import os


class FeaKeywordsExtractor:
    def __init__(self):
        self.logger = logger
        self.fea_keywords_translator = fea_keywords_translator

    def extract(self, *args, **kwargs):
        file_path = kwargs.get("file_path", args[0] if len(args) > 0 else None)
        solver1 = kwargs.get("solver1", args[1] if len(args) > 1 else None)
        version1 = kwargs.get("version1", args[2] if len(args) > 2 else None)

        if os.path.isfile(file_path):
            dataframe = self.parse_file(file_path=file_path, solver1=solver1, version1=version1)
            self.extract_part_info(dataframe=dataframe, file_path=file_path)

        elif os.path.isdir(file_path):

            for file in os.listdir(file_path):

                name, ext = os.path.splitext(file)

                if ext.lower() == ".k" or ext.lower() == ".key":

                    full_path = os.path.join(file_path, file)

                    dataframe = self.parse_file(file_path=full_path, solver1=solver1, version1=version1)
                    self.extract_part_info(dataframe=dataframe, file_path=full_path)

    def parse_file(self, file_path, solver1, version1):
        self.fea_keywords_translator.translate(
            file_path=file_path,
            solver1=solver1,
            version1=version1,
            solver2="parse_only",
            version2="0.0"
        )

        dataframe = self.fea_keywords_translator.dataframe

        return dataframe

    def extract_part_info(self, dataframe, file_path):
        node_tensor = dataframe.node_tensor
        element_shell_tensor = dataframe.element_shell_tensor
        element_solid_surface_tensor = dataframe.element_solid_surface_tensor

        if len(element_shell_tensor) > 0 or len(element_solid_surface_tensor) > 0:
            all_shell_element = tbox.concatenate_shell_solid_surfaces(elements_shell=element_shell_tensor,
                                                                      solid_surfaces=element_solid_surface_tensor)

            part_name_mapping = dataframe.part_name_mapping

            part_info_dict = tbox.get_part_info(nodes=node_tensor,
                                                shells=all_shell_element,
                                                part_name_mapping=part_name_mapping)

            tbox.save(file_path=file_path,
                      source_dict=part_info_dict)

            self.logger.info(f"original file: {file_path}")
            self.logger.info(f"saved successfully in {os.path.dirname(file_path)}\n")


fea_keywords_extractor = FeaKeywordsExtractor()
