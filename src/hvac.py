import os, subprocess, sys
from io import StringIO
from typing import Dict, List
from eppy import modeleditor
from eppy.modeleditor import IDF
from recipes import copy_idf_objects, read_json

IDF.setiddname("../resources/Energy+V9_0_1.idd")


class HVAC:
    """ v1: Add HVAC unitary system to zones
        v2: Use OpenStudio ruby call to add package single zone air conditioner (more system types to come)
    """

    hvac_settings = read_json("hvac_settings.json")
    hvac_dev_folder_name = hvac_settings["hvac_intermediate_folder_name"]

    def __init__(self, case: Dict, idf: IDF):
        self.idf = idf
        self.case = case
        self.hvac_type = self.case["hvac"]["hvac_type"]
        self.pure_hvac_objs = None
        self.exc_obj_types = None

        # run modeling strategy
        self.generate_osstd_input_idf()
        self.run_osstd_rubycall()
        self.clean_up_save_add_osstd_output()
        self.add_misc_hvac_objs()

    def generate_osstd_input_idf(self):
        exc_hvac_meta = read_json(
            self.hvac_settings["excluded_osstd_hvac_obj_types_file_path"]
        )
        self.exc_obj_types = [ot.upper().strip() for ot in exc_hvac_meta[self.hvac_type]]

        zones_idf = IDF(StringIO(""))
        zones_idf_obj_types = [ot.upper().strip() for ot in self.hvac_settings["idf_obj_types_for_osstd_use"]]

        objs = []
        for obj_type in zones_idf_obj_types:
            objs.extend(list(self.idf.idfobjects[obj_type]))
            if obj_type not in self.exc_obj_types:
                self.exc_obj_types.append(
                    obj_type
                )  # add osstd input idf obj types to excluded list if not there already

        for obj in objs:
            zones_idf.copyidfobject(obj)
        zones_idf.saveas(f"../{self.hvac_dev_folder_name}/zones.idf")

    def run_osstd_rubycall(self):
        ruby_run = ["ruby", "generate_hvac.rb"]
        run_proc = subprocess.run(ruby_run, capture_output=True)
        print("\nSTDOUT:")
        print(run_proc.stdout.decode("utf-8"))
        print("\nSTDERR")
        print(run_proc.stderr.decode("utf-8"))
        osstd_hvacadded = IDF(f"../{self.hvac_dev_folder_name}/zones_hvacadded.idf")
        print(self.exc_obj_types)
        self.pure_hvac_objs = self.get_object_not_in_types(
            osstd_hvacadded, self.exc_obj_types
        )
        self.exc_objs = self.get_object_by_types(osstd_hvacadded, self.exc_obj_types)

    def clean_up_save_add_osstd_output(self):
        for obj in self.pure_hvac_objs:
            for field in obj.__dict__["objls"]:
                if " Thermal Zone" in str(obj[field]):
                    obj[field] = obj[field].replace(
                        " Thermal Zone", ""
                    )  # take out 'thermal zone' in names/refs

        hvac_pure = IDF(StringIO(""))
        for obj in self.pure_hvac_objs:
            hvac_pure.copyidfobject(obj)
        hvac_pure.saveas(f"../{self.hvac_dev_folder_name}/hvac_pure.idf")

        exc_objs_idf = IDF(StringIO(""))
        for obj in self.exc_objs:
            exc_objs_idf.copyidfobject(obj)
        exc_objs_idf.saveas(f"../{self.hvac_dev_folder_name}/exc_objs.idf")

        self.idf = copy_idf_objects(self.idf, hvac_pure)

    def add_misc_hvac_objs(self):
        # add thermostat
        zonelist_name = self.idf.idfobjects["ZONELIST"][0].Name
        zonecontrol_thermostat_dict = {
            "key": "ZoneControl:Thermostat".upper(),
            "Name": f"{zonelist_name} Thermostat",
            "Zone_or_ZoneList_Name": zonelist_name,
            "Control_Type_Schedule_Name": f"{zonelist_name} Thermostat Thermostat Schedule",
            "Control_1_Object_Type": "ThermostatSetpoint:DualSetpoint",
            "Control_1_Name": f"{zonelist_name} Thermostat Thermostat DualSP",
        }
        self.idf.newidfobject(**zonecontrol_thermostat_dict)

        thermostatsetpoint_dualsetpoint_dict = {
            "key": "ThermostatSetpoint:DualSetpoint".upper(),
            "Name": f"{zonelist_name} Thermostat Thermostat DualSP",
            "Heating_Setpoint_Temperature_Schedule_Name": f"{zonelist_name} Htg Thermostat Schedule",
            "Cooling_Setpoint_Temperature_Schedule_Name": f"{zonelist_name} Clg Thermostat Schedule",
        }
        self.idf.newidfobject(**thermostatsetpoint_dualsetpoint_dict)

        # add thermostat schedule
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
            self.idf.newidfobject(**one_dict)

        # add oa design specification
        oa_dict = {
            "key": "DESIGNSPECIFICATION:OUTDOORAIR",
            "Name": "design_oa",
            "Outdoor_Air_Method": "Sum",
            "Outdoor_Air_Flow_per_Person": 0.00236,
            "Outdoor_Air_Flow_per_Zone_Floor_Area": 0.0003,
        }

        self.idf.newidfobject(**oa_dict)

        for sizingzone in self.idf.idfobjects["SIZING:ZONE"]:
            sizingzone["Design_Specification_Outdoor_Air_Object_Name"] = "design_oa"

        # TODO: modify schedule

    def get_containing_object_types(self, idf: IDF) -> List:
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

    def get_object_by_types(self, idf: IDF, types: List, ignore_error=True) -> List:
        types = [type.upper().strip() for type in types]
        all_objs = []
        for type in types:
            objs = idf.idfobjects[type.upper().strip()]
            if len(objs) == 0 and (not ignore_error):
                print(f"ERROR: {type} does not exist in the idf")
                continue
            all_objs.extend(list(objs))
        return all_objs

    def get_object_not_in_types(self, idf: IDF, types: List) -> List:
        types = [type.upper().strip() for type in types]
        exc_objs = []
        all_types = self.get_containing_object_types(idf)
        for type in all_types:
            if type not in types:
                objs = idf.idfobjects[type.upper().strip()]
                if len(objs) == 0:
                    print("Somthing is wrong!")
                    continue
                exc_objs.extend(list(objs))
        return exc_objs

    def save_idf(self, path):
        self.idf.saveas(path, lineendings="unix")


def main():

    testidf = IDF("../hvac_dev/loads_added.idf")
    test_proc_case = {"hvac": {"hvac_type": "PSZ:AC"}}

    hvacadded_obj = HVAC(test_proc_case, testidf)
    hvacadded_obj.save_idf("../hvac_dev/hvacadded.idf")

if __name__ == "__main__":
    main()
