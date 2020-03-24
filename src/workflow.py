"""Illustrate process, dev use only"""

#%%
import os

os.chdir("/mnt/c/FirstClass/airflow/dags/urban-sim-flow/src") # for linux
# os.chdir('C:\\FirstClass\\airflow\\dags\\urban-sim-flow\\src') # for windows
from io import StringIO
from typing import Dict
import pandas as pd
from geomeppy import IDF
import json
from geometry import Geometry
from preprocessor import Preprocessor
from schedule import Schedule
import recipes

IDF.setiddname("../resources/Energy+V9_0_1.idd")


#%% load minimal idf
idf1 = IDF("../resources/idfs/Minimal.idf")
idf2 = IDF("../resources/idfs/Minimal.idf")

#%% convert units

with open("../input/raw_inputs/case1.json") as f:
    case1 = json.load(f)

with open("../input/raw_inputs/case2.json") as f:
    case2 = json.load(f)

case1_conv = recipes.convert_dict_unit(case1)
case2_conv = recipes.convert_dict_unit(case2)

with open("../input/processed_inputs/case1.json", "w") as f:
    f.write(json.dumps(case1_conv, indent=4))

with open("../input/processed_inputs/case2.json", "w") as f:
    f.write(json.dumps(case2_conv, indent=4))

#%% preprocessors
proc_case1 = Preprocessor(case1_conv).case_proc
with open("../input/processed_inputs/case1-processed.json", "w") as f:
    f.write(json.dumps(proc_case1, indent=4))

proc_case2 = Preprocessor(case1_conv).case_proc
with open("../input/processed_inputs/case2-processed.json", "w") as f:
    f.write(json.dumps(proc_case2, indent=4))

#%% geometry processor

idf1 = Geometry(proc_case1, idf1)
idf2 = Geometry(proc_case2, idf2)


#%% geometry output
idf1.save_idf("../devoutput/geometryadded1.idf")
idf2.save_idf("../devoutput/geometryadded2.idf")

# %% schedule processor
with open("../input/processed_inputs/std_schedule_dev.json") as f:
    idf1_scheduleadded = Schedule(json.load(f), idf1.idf)
idf1_scheduleadded.save_idf("../devoutput/scheduleadded1.idf")


# %%
