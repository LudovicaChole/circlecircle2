import os
from core.hmdesktop.hm_scripts.header import header
from core.hmdesktop.hm_scripts.success_signal import success_signal
from core.hmdesktop.hm_scripts.import_geometry import import_geometry
from core.hmdesktop.hm_scripts.import_hm import import_hm
from core.hmdesktop.hm_scripts.save_as import save_as


class ScriptsGenerator:
    def __init__(self):
        self.support_script = 1
        self.header = header
        self.success_signal = success_signal
        self.import_geometry = import_geometry
        self.import_hm = import_hm
        self.save_as = save_as

    def write_script(self, temp_folder, mode, target_path, runhwxlog_path):
        # STP
        if mode == "run_background_stp":
            hm_scripts_path = os.path.join(temp_folder, "hm_scripts.py")

            with open(hm_scripts_path, "w", encoding="utf-8", errors="ignore") as f:
                f.write(self.header(temp_folder=temp_folder, runhwxlog_path=runhwxlog_path))
                f.write(self.import_geometry(stp_path=target_path))
                f.write(self.save_as(target_path=target_path, runhwxlog_path=runhwxlog_path))

            return hm_scripts_path

        # HM File
        elif mode == "run_background_hm":
            hm_scripts_path = os.path.join(temp_folder, "hm_scripts.py")

            with open(hm_scripts_path, "w", encoding="utf-8", errors="ignore") as f:
                f.write(self.header(temp_folder=temp_folder, runhwxlog_path=runhwxlog_path))
                f.write(self.import_hm(hm_path=target_path))
                f.write(self.save_as(target_path=target_path, runhwxlog_path=runhwxlog_path))

            return hm_scripts_path

        # GUI FEA KEYWORDS
        elif mode == "launch_key":
            hm_scripts_path = os.path.join(temp_folder, "hm_scripts.py")

            with open(hm_scripts_path, "w", encoding="utf-8", errors="ignore") as f:
                f.write(self.header(temp_folder=temp_folder, runhwxlog_path=runhwxlog_path))
                f.write(self.success_signal(temp_folder=temp_folder))

            return hm_scripts_path

        # GUI HM
        elif mode == "launch_hm":
            pass
