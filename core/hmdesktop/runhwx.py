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
from core.hmdesktop.scripts_generator import ScriptsGenerator


class RunHWX:
    def __init__(self, hwx_path, temp_folder):
        self.hwx_path = hwx_path
        self.temp_folder = temp_folder
        self.scripts_generator = ScriptsGenerator()
        self.runhwxlog_path = os.path.join(self.temp_folder, 'runhwx.log')

    def run_background(self, mode, target_path):

        hw_script_path = self.scripts_generator.write_script(temp_folder=self.temp_folder,
                                                             mode=mode,
                                                             target_path=target_path,
                                                             runhwxlog_path=self.runhwxlog_path)

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
        run_bat_path = os.path.join(self.temp_folder, "RunHWX.bat")

        with open(run_bat_path, "w", encoding="utf-8", errors="ignore") as f:
            f.write(run_code)

        subprocess.run(run_bat_path, shell=True, capture_output=True, text=True)

        hwx_command_path = os.path.join(self.temp_folder, "command1.tcl")

        if os.path.exists(run_bat_path):
            os.remove(run_bat_path)

        if os.path.exists(hwx_command_path):
            os.remove(hwx_command_path)

    def launch_hmdesktop(self, mode, target_path):
        hw_script_path = self.scripts_generator.write_script(temp_folder=self.temp_folder,
                                                             mode=mode,
                                                             target_path=target_path,
                                                             runhwxlog_path=self.runhwxlog_path)

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

        run_bat_path = os.path.join(self.temp_folder, "RunHWX.bat")
        success_signal_path = os.path.join(self.temp_folder, "success.success")

        with open(run_bat_path, "w", encoding="utf-8", errors="ignore") as f:
            f.write(run_code)

        subprocess.Popen(run_bat_path)

        while True:
            if os.path.exists(success_signal_path):
                os.remove(success_signal_path)
                os.remove(run_bat_path)
                os.remove(hw_script_path)
                break

            time.sleep(2)


hwx_path = r"D:\Program Files\Altair\2026\hwdesktop\hwx\bin\win64\runhwx.exe"
temp_folder = r"D:\Work\WJD\P200_PyProject\Test_Data\runhwx"
stp_path = r"D:\Work\WJD\P200_PyProject\Test_Data\test_banjin.stp"
hm_path = r"D:\Work\WJD\P200_PyProject\Test_Data\test_banjin_c2auto.hm"

text_runhwx = RunHWX(hwx_path, temp_folder)
text_runhwx.run_background(mode="run_background_hm", target_path=hm_path)
