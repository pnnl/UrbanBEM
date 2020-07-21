"""Illustrate process, dev use only

modified to accomodate single idf file, aiming at being called in a streamline.
"""

#%%
import os

os.chdir("/mnt/c/FirstClass/airflow/dags/urban-sim-flow/src")  # for linux
# os.chdir('C:\\FirstClass\\airflow\\dags\\urban-sim-flow\\src') # for windows

from geomeppy import IDF
import json
from geometry import Geometry
from constructions import Constructions
from loads import Loads
from preprocessor import Preprocessor
from schedule import Schedule
from hvac import HVAC
import recipes

IDF.setiddname("../resources/Energy+V9_0_1.idd")

#%% case name
casename = "cbecs3"


#%% load minimal idf
idf = IDF("../resources/idfs/Minimal.idf")
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
geometryadded_obj = Geometry(proc_case, idf)
geometryadded_obj.save_idf("../devoutput/geometry_added.idf")

#%% construction processor
constructionadded_obj = Constructions(proc_case, geometryadded_obj.idf)
constructionadded_obj.save_idf("../devoutput/construction_added.idf")

# %% schedule processor
scheduleadded_obj = Schedule(proc_case, constructionadded_obj.idf)
scheduleadded_obj.save_idf("../devoutput/schedule_added.idf")

# %% load processor
loadadded_obj = Loads(proc_case, scheduleadded_obj.idf)
loadadded_obj.save_idf("../devoutput/loads_added.idf")

# %% hvac processor
hvacadded_obj = HVAC(proc_case, loadadded_obj.idf)
hvacadded_obj.save_idf("../devoutput/hvac_added.idf")