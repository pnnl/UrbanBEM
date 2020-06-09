#%%
import os, subprocess
from io import StringIO
from typing import List


from tqdm import tqdm

os.chdir("/mnt/c/FirstClass/airflow/dags/urban-sim-flow/src")  # for linux
# os.chdir('C:\\FirstClass\\airflow\\dags\\urban-sim-flow\\src') # for windows

from geomeppy import IDF
import json

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


def get_object_by_types(idf: IDF, types: List, ignore_error=True) -> List:
    all_objs = []
    for type in types:
        objs = idf.idfobjects[type.upper().strip()]
        if len(objs) == 0 and (not ignore_error):
            print(f"ERROR: {type} does not exist in the idf")
            continue
        all_objs.extend(list(objs))
    return all_objs


def get_object_not_in_types(idf: IDF, types: List) -> List:
    exc_objs = []
    all_types = get_containing_object_types(idf)
    for type in all_types:
        if type not in types:
            objs = idf.idfobjects[type.upper().strip()]
            if len(objs) == 0:
                print("Somthing is wrong!")
                continue
            exc_objs.extend(list(objs))
    return exc_objs


#%% load idf
original_idf = IDF("../hvac_dev/loads_added.idf")
casename = "cbecs1"
case_path = f"../input/processed_inputs/{casename}.json"
with open(case_path) as f:
    proc_case = json.load(f)

#%% get needed objs (also add them to the excluded objects list)

with open("../resources/exc_osstd_hvac_objtypes_meta.json") as f:
    exc_hvac_meta = json.load(f)
exc_obj_types = exc_hvac_meta["PSZ:AC"]

zones_idf = IDF(StringIO(""))
zones_idf_obj_types = [
    "Zone",
    "SizingPeriod:DesignDay",
    "Building",
    "GlobalGeometryRules",
]
zones_idf_obj_types = [one.upper() for one in zones_idf_obj_types]

objs = []
for obj_type in zones_idf_obj_types:
    objs.extend(list(original_idf.idfobjects[obj_type]))
    if obj_type not in exc_obj_types:
        exc_obj_types.append(obj_type)

for obj in objs:
    zones_idf.copyidfobject(obj)
zones_idf.saveas("../hvac_dev/zones.idf")

#%% run osstd method from ruby
ruby_run = ["ruby", "generate_hvac.rb"]

run_proc = subprocess.run(ruby_run, capture_output=True)
print("\nSTDOUT:")
print(run_proc.stdout.decode("utf-8"))
print("\nSTDERR")
print(run_proc.stderr.decode("utf-8"))

#%% read os output idfs
zones_translated = IDF("../hvac_dev/zones_translated.idf")
zones_hvacadded = IDF("../hvac_intermediate/osstd_hvacadded.idf")

#%%
zones_idf_objtypes = get_containing_object_types(zones_idf)
zones_translated_objtypes = get_containing_object_types(zones_translated)
zones_hvacadded_objtypes = get_containing_object_types(zones_hvacadded)

#%%

objs = get_object_not_in_types(zones_hvacadded, exc_obj_types)

#%% take out 'thermal zone' in names/refs
for obj in tqdm(objs):
    for field in obj.__dict__["objls"]:
        if " Thermal Zone" in str(obj[field]):
            obj[field] = obj[field].replace(" Thermal Zone", "")


#%% output hvac objs for dev
hvac_pure = IDF(StringIO(""))
for obj in tqdm(objs):
    hvac_pure.copyidfobject(obj)
hvac_pure.saveas("../hvac_dev/hvac_pure.idf")

#%%
# TODO: reload original idf to make sure it is clean (no need for non-dev)
original_idf = IDF("../devoutput/loads_added.idf")
for obj in tqdm(objs):
    original_idf.copyidfobject(obj)

#%% add thermostat
zonelist_name = original_idf.idfobjects["ZONELIST"][0].Name

zonecontrol_thermostat_dict = {
    "key": "ZoneControl:Thermostat".upper(),
    "Name": f"{zonelist_name} Thermostat",
    "Zone_or_ZoneList_Name": zonelist_name,
    "Control_Type_Schedule_Name": f"{zonelist_name} Thermostat Thermostat Schedule",
    "Control_1_Object_Type": "ThermostatSetpoint:DualSetpoint",
    "Control_1_Name": f"{zonelist_name} Thermostat Thermostat DualSP",
}
original_idf.newidfobject(**zonecontrol_thermostat_dict)

thermostatsetpoint_dualsetpoint_dict = {
    "key": "ThermostatSetpoint:DualSetpoint".upper(),
    "Name": f"{zonelist_name} Thermostat Thermostat DualSP",
    "Heating_Setpoint_Temperature_Schedule_Name": f"{zonelist_name} Htg Thermostat Schedule",
    "Cooling_Setpoint_Temperature_Schedule_Name": f"{zonelist_name} Clg Thermostat Schedule",
}
original_idf.newidfobject(**thermostatsetpoint_dualsetpoint_dict)

thermostat_schedules_dict_list = [
    {
        "key": "Schedule:Compact".upper(),
        "Name": f"{zonelist_name} Thermostat Thermostat Schedule",
        "Field_1": "Through: 12/31",
        "Field_2": "For: AllDays",
        "Field_3": "Until: 24:00",
        "Field_4": 4,
    },
    {
        "key": "Schedule:Compact".upper(),
        "Name": f"{zonelist_name} Htg Thermostat Schedule",
        "Field_1": "Through: 12/31",
        "Field_2": "For: AllDays",
        "Field_3": "Until: 24:00",
        "Field_4": 18,
    },
    {
        "key": "Schedule:Compact".upper(),
        "Name": f"{zonelist_name} Clg Thermostat Schedule",
        "Field_1": "Through: 12/31",
        "Field_2": "For: AllDays",
        "Field_3": "Until: 24:00",
        "Field_4": 26,
    },
]
for one_dict in thermostat_schedules_dict_list:
    original_idf.newidfobject(**one_dict)

oa_dict = {
    "key": "DESIGNSPECIFICATION:OUTDOORAIR",
    "Name": "design_oa",
    "Outdoor_Air_Method": "Sum",
    "Outdoor_Air_Flow_per_Person": 0.00236,
    "Outdoor_Air_Flow_per_Zone_Floor_Area": 0.0003,
}

original_idf.newidfobject(**oa_dict)

for sizingzone in original_idf.idfobjects["SIZING:ZONE"]:
    sizingzone["Design_Specification_Outdoor_Air_Object_Name"] = "design_oa"


#%%
# TODO: fix shgc random number caused fatal fault (if > 7) (temporary)
original_idf.idfobjects["WINDOWMATERIAL:SIMPLEGLAZINGSYSTEM"][0]["UFactor"] = 3

#%%
original_idf.saveas("../hvac_dev/hvacadded.idf")

#%% have a peek on the excluded objects
# exc_objs = get_object_not_in_types(zones_hvacadded, hvac_meta["PSZ:AC"])
exc_objs = get_object_by_types(zones_hvacadded, exc_obj_types)
exc_idf = IDF(StringIO(""))
for obj in tqdm(exc_objs):
    exc_idf.copyidfobject(obj)
exc_idf.saveas("../hvac_dev/exc_objs.idf")
