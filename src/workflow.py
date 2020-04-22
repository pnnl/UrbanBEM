"""Illustrate process, dev use only

modified to accomodate single idf file, aiming at being called in a streamline.
"""

#%%
import os

os.chdir("/mnt/c/FirstClass/airflow/dags/urban-sim-flow/src")  # for linux
# os.chdir('C:\\FirstClass\\airflow\\dags\\urban-sim-flow\\src') # for windows
from io import StringIO
from typing import Dict
import pandas as pd
from geomeppy import IDF
import json
from geometry import Geometry
from loads import Loads
from preprocessor import Preprocessor
from schedule import Schedule
from hvac import HVAC
import recipes

IDF.setiddname("../resources/Energy+V9_0_1.idd")


#%% load minimal idf
idf = IDF("../resources/idfs/Minimal.idf")
casename = 'cbecs4'
case_path = f"../input/std_json_raw/{casename}.json"

#%% convert units

with open(case_path) as f:
    case = json.load(f)

case_conv, case_conv_clean = recipes.convert_dict_unit(case)

with open(f"../input/std_json_conv/{casename}_conv.json", "w") as f:
    f.write(json.dumps(case_conv, indent=4))
with open(f"../input/std_json_conv_clean/{casename}_conv.json", "w") as f:
    f.write(json.dumps(case_conv_clean, indent=4))


#%% preprocessors
proc_case = Preprocessor(case_conv_clean).case_proc
with open(f"../input/processed_inputs/{casename}_processed.json", "w") as f:
    f.write(json.dumps(proc_case, indent=4))

#%% geometry processor

idf = Geometry(proc_case, idf)

#%% geometry output
idf.save_idf("../devoutput/geometry_added.idf")

# %% schedule processor
with open("../input/processed_inputs/std_hvac_dev.json") as f:
    idf1_scheduleadded = Schedule(json.load(f), idf1.idf)
idf1_scheduleadded.save_idf("../devoutput/scheduleadded1.idf")

# %% load processor
# Read output from previous processor
with open("../input/processed_inputs/std_hvac_dev.json") as f:
    idf1_lds = Loads(json.load(f), idf1_scheduleadded.idf)
idf1_lds.save_idf("../devoutput/loadsadded1.idf")


# %% hvac processor
with open("../input/processed_inputs/std_hvac_dev.json") as f:
    idf1_hvacadded = HVAC(json.load(f), idf1_lds.idf)
idf1_hvacadded.save_idf("../devoutput/hvacadded1.idf")
