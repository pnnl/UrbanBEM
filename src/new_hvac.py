#%%
import os
from io import StringIO
from typing import List

from tqdm import tqdm

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

#%% helper
def get_containing_object_types(idf: IDF) -> List:
    results = []
    totalnum = 0
    for key, val in idf.idfobjects.items():
        if len(val) > 0:
            results.append(key)
            print(f"{key}: {len(val)}")
            totalnum += len(val)
    print(f"Total number of objects: {totalnum}")
    print("\n **** \n")
    return results


#%%


def get_object_by_types(idf: IDF, types: List, ignore_error=True):
    all_objs = []
    for type in types:
        objs = idf.idfobjects[type.upper().strip()]
        if len(objs) == 0 and (not ignore_error):
            print(f"ERROR: {type} does not exist in the idf")
            continue
        all_objs.extend(list(objs))
    return all_objs


#%% load idf
original_idf = IDF("../devoutput/loads_added.idf")
casename = "cbecs1"
case_path = f"../input/processed_inputs/{casename}.json"
with open(case_path) as f:
    proc_case = json.load(f)

#%% get zones
zones = original_idf.idfobjects["ZONE"]
zones_idf = IDF(StringIO(""))
for obj in zones:
    zones_idf.copyidfobject(obj)
zones_idf.saveas("../hvac_dev/zones.idf")

#%% read os output idfs
zones_translated = IDF("../hvac_dev/zones_translated.idf")
zones_hvacadded = IDF("../hvac_dev/zones_hvacadded.idf")

#%%
zones_idf_objtypes = get_containing_object_types(zones_idf)
zones_translated_objtypes = get_containing_object_types(zones_translated)
zones_hvacadded_objtypes = get_containing_object_types(zones_hvacadded)

#%%
with open("../resources/osstd_hvac_objtypes_meta.json") as f:
    hvac_meta = json.load(f)

objs = get_object_by_types(zones_hvacadded, hvac_meta["PSZ:AC"], ignore_error=False)

#%% take out 'thermal zone' in names/refs
for obj in tqdm(objs):
    for field in obj.__dict__["objls"]:
        if " Thermal Zone" in str(obj[field]):
            obj[field] = obj[field].replace(" Thermal Zone", "")


#%%
for obj in tqdm(objs):
    original_idf.copyidfobject(obj)


#%%
original_idf.saveas("../hvac_dev/hvacadded.idf")
