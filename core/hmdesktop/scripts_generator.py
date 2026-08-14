import os
from core.hmdesktop.hm_scripts.header import header
from core.hmdesktop.hm_scripts.success_signal import success_signal
from core.hmdesktop.hm_scripts.import_geometry import import_geometry
from core.hmdesktop.hm_scripts.import_hm import import_hm
from core.hmdesktop.hm_scripts.import_key import import_key
from core.hmdesktop.hm_scripts.set_display_2 import set_display_2
from core.hmdesktop.hm_scripts.set_display_3 import set_display_3
from core.hmdesktop.hm_scripts.get_component_info import get_component_info    # Available Parameter: components_collection
from core.hmdesktop.hm_scripts.get_solid_info import get_solid_info
from core.hmdesktop.hm_scripts.set_component_cardimage_to_part import set_component_cardimage_to_part
from core.hmdesktop.hm_scripts.save_as import save_as
from core.hmdesktop.hm_scripts.write_exception import write_exception


class ScriptsGenerator:
    def __init__(self):
        self.support_script = 1

        self.header = header
        self.success_signal = success_signal

        self.import_geometry = import_geometry
        self.import_hm = import_hm
        self.import_key = import_key
        self.set_display_2 = set_display_2
        self.set_display_3 = set_display_3
        self.get_component_info = get_component_info
        self.get_solid_info = get_solid_info

        self.set_component_cardimage_to_part = set_component_cardimage_to_part

        self.save_as = save_as
        self.write_exception = write_exception

    def write_script(self, work_dictionary, mode, target, run_hwx_log):
        # Global Parameter -->

        # work_dictionary;
        # run_hwx_log;
        # script_data;
        # script_data_file;
        # target;
        # target_folder;
        # target_name;
        # save_as_file;

        hm_scripts_path = os.path.join(work_dictionary, "hm_scripts.py")

        # STP
        if mode == "run_background_stp":

            with open(hm_scripts_path, "w", encoding="utf-8", errors="ignore") as f:
                f.write(self.header(work_dictionary=work_dictionary, run_hwx_log=run_hwx_log, target=target))
                f.write(self.import_geometry())
                f.write(self.get_component_info())
                f.write(self.set_component_cardimage_to_part())
                f.write(self.save_as())
                f.write(self.success_signal())
                f.write(self.write_exception())

            return hm_scripts_path

        # HM File
        elif mode == "run_background_hm":

            with open(hm_scripts_path, "w", encoding="utf-8", errors="ignore") as f:
                f.write(self.header(work_dictionary=work_dictionary, run_hwx_log=run_hwx_log, target=target))
                f.write(self.import_hm())
                f.write(self.save_as())

            return hm_scripts_path

        # GUI FEA KEYWORDS
        elif mode == "launch_key":

            with open(hm_scripts_path, "w", encoding="utf-8", errors="ignore") as f:
                f.write(self.header(work_dictionary=work_dictionary, run_hwx_log=run_hwx_log, target=target))
                f.write(self.success_signal())
                f.write(self.import_key())
                f.write(self.set_display_3())
                f.write(self.save_as())

            return hm_scripts_path

        # GUI HM
        elif mode == "launch_hm":

            with open(hm_scripts_path, "w", encoding="utf-8", errors="ignore") as f:
                f.write(self.header(work_dictionary=work_dictionary, run_hwx_log=run_hwx_log, target=target))
                f.write(self.success_signal())
                f.write(self.import_hm())
                f.write(self.set_display_3())
                f.write(self.save_as())

            return hm_scripts_path
