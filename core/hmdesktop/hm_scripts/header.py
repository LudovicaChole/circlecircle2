def header(temp_folder, runhwxlog_path):
    h1 = r"$$ ============================================================\n$$ RUNHWX Log\n$$ \n"
    h2 = r"$$ DATE: {time_string}\n$$ \n$$ ============================================================\n$$\n$$\n"

    code = f"""import hm
import hm.entities as ent
import os
import time
from datetime import datetime

model = hm.Model()

temp_folder = r'{temp_folder}'
now = datetime.now()
time_string = now.strftime("%Y-%M-%D %H:%M:%S")

with open(r'{runhwxlog_path}', "w", encoding="utf-8") as f:
    f.write(f'{h1}')
    f.write(f'{h2}')

##
##
##
##

"""
    return code
