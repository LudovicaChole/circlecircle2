"""
Run automatically by CMD

[1] Run HWX background

@echo off

setlocal

set "RUNHWX=D:\Program Files\Altair\2026\hwdesktop\hwx\bin\win64\runhwx.exe"
set "HM_SCRIPT=D:\Work\WJD\P200_PyProject\circlecircle2\core\hmdesktop\runhwx.py"

"%RUNHWX%" ^
-cfg ^
-client HyperWorksDesktop ^
-plugin HyperworksGeneral ^
-profile HyperworksGeneral ^
-l en ^
-startwith HyperMesh ^
-b ^
-f %HM_SCRIPT%


[2] Launch HyperMesh

@echo off

setlocal

set "RUNHWX=D:\Program Files\Altair\2026\hwdesktop\hwx\bin\win64\runhwx.exe"

"%RUNHWX%" ^
-client HyperWorksDesktop ^
-plugin HyperworksGeneral ^
-profile HyperworksGeneral ^
-l en ^
-startwith HyperMesh

"""
import os
import subprocess
import time
from utilities.logger import logger
from core.hmdesktop.scripts_generator import ScriptsGenerator


class RunHWX:
    def __init__(self, hwx_path, work_dictionary):
        self.hwx_path = hwx_path
        self.work_dictionary = work_dictionary
        self.scripts_generator = ScriptsGenerator()
        self.logger = logger
        self.run_hwx_log = os.path.join(self.work_dictionary, 'runhwx.log')

    def run_background(self, mode, target):

        hw_script_path = self.scripts_generator.write_script(work_dictionary=self.work_dictionary,
                                                             mode=mode,
                                                             target=target,
                                                             run_hwx_log=self.run_hwx_log)

        run_code = f"""
@echo off

echo ============================================================
echo HyperMesh 2026 Python Batch
echo ============================================================
echo RUNHWX={self.hwx_path}
echo This windows will close if RUNHWX is closed

setlocal

set "RUNHWX={self.hwx_path}"
set "HM_SCRIPT={hw_script_path}"

"%RUNHWX%" ^
-cfg ^
-client HyperWorksDesktop ^
-plugin HyperworksGeneral ^
-profile HyperworksGeneral ^
-l en ^
-startwith HyperMesh ^
-b ^
-f %HM_SCRIPT%

"""
        run_bat_path = os.path.join(self.work_dictionary, "RunHWX.bat")
        success_signal_path = os.path.join(self.work_dictionary, "success.success")

        with open(run_bat_path, "w", encoding="utf-8", errors="ignore") as f:
            f.write(run_code)

        self.logger.info(f"RUNHWX is processing at background, please wait ...\n")
        self.logger.info(f"RUNHWX may take a few minutes...\n")

        subprocess.run(run_bat_path, shell=True, capture_output=True, text=True)
        # subprocess.Popen(run_bat_path)

        hwx_command_path = os.path.join(self.work_dictionary, "command1.tcl")

        if os.path.exists(self.run_hwx_log):
            with open(self.run_hwx_log, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    self.logger.info(line)

            self.logger.info(f"All processes have been completed\n")
        else:
            self.logger.error(f"runhwx.log is not found, please check again\n")

        if os.path.exists(run_bat_path):
            os.remove(run_bat_path)

        if os.path.exists(hwx_command_path):
            os.remove(hwx_command_path)

        if os.path.exists(hw_script_path):
            os.remove(hw_script_path)

    def launch_hmdesktop(self, mode, target):
        hw_script_path = self.scripts_generator.write_script(work_dictionary=self.work_dictionary,
                                                             mode=mode,
                                                             target=target,
                                                             run_hwx_log=self.run_hwx_log)

        run_code = f"""
@echo off

setlocal

set "RUNHWX={self.hwx_path}"
set "HM_SCRIPT={hw_script_path}"

"%RUNHWX%" ^
-client HyperWorksDesktop ^
-plugin HyperworksGeneral ^
-profile HyperworksGeneral ^
-l en ^
-startwith HyperMesh ^
-f %HM_SCRIPT%
"""

        run_bat_path = os.path.join(self.work_dictionary, "RunHWX.bat")
        success_signal_path = os.path.join(self.work_dictionary, "success.success")

        with open(run_bat_path, "w", encoding="utf-8", errors="ignore") as f:
            f.write(run_code)

        subprocess.Popen(run_bat_path)

        print(f"File {target} is opened in HyperMesh\n")

        hwx_command_path = os.path.join(self.work_dictionary, "command1.tcl")

        while True:
            if os.path.exists(success_signal_path):
                os.remove(success_signal_path)

                if os.path.exists(run_bat_path):
                    os.remove(run_bat_path)

                if os.path.exists(hw_script_path):
                    os.remove(hw_script_path)

                if os.path.exists(hwx_command_path):
                    os.remove(hwx_command_path)

                break

            time.sleep(2)


hwx_path = r"C:\Program Files\Altair\2026\hwdesktop\hwx\bin\win64\runhwx.exe"
temp_folder = r"E:\PythonProject\test_hwx"
stp_path = r"E:\PythonProject\test_hwx\Part1.stp"
hm_path = r"E:\PythonProject\test_hwx\761D_Outer_Beam_c2auto.hm"
fea_path = r"E:\PythonProject\test_hwx\761D_Outer_Beam.k"

runhwx = RunHWX(hwx_path, temp_folder)
runhwx.run_background(mode="run_background_stp", target=stp_path)
# runhwx.run_background(mode="run_background_hm", target=hm_path)
# runhwx.launch_hmdesktop(mode="launch_key", target=fea_path)
# runhwx.launch_hmdesktop(mode="launch_hm", target=hm_path)
