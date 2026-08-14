def header(work_dictionary, run_hwx_log, target):
    h1 = r"$$ ============================================================\n$$\n$$ RUNHWX Log\n$$ \n"
    h2 = r"$$ DATE: {time_string}\n$$ \n$$ ============================================================\n$$\n$$\n"

    code = f"""import hm
import hm.entities as ent
import os
import time
import json
import traceback
from datetime import datetime

model = hm.Model()

work_dictionary = r'{work_dictionary}'
run_hwx_log = r'{run_hwx_log}'
script_data = {dict()}
script_data_file = os.path.join(work_dictionary, "data.json")
target = r'{target}'

target_folder = os.path.dirname(r'{target}')

target_basename = os.path.basename(r'{target}')
target_name, target_ext = os.path.splitext(target_basename)

save_as_file = os.path.join(target_folder, target_name+"_c2auto.hm")

now = datetime.now()
time_string = now.strftime("%Y-%M-%D %H:%M:%S")

try:
    with open(run_hwx_log, "a", encoding="utf-8") as f:
        f.write(f'{h1}')
        f.write(f'{h2}')

##
##
##
##

"""
    return code
