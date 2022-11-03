import os, subprocess, sys, math
from io import StringIO
from typing import Dict, List
from eppy import modeleditor
from eppy.modeleditor import IDF
from recipes import (
    copy_idf_objects,
    read_json,
    batch_modify_idf_objs,
    get_containing_object_types,
    get_object_by_types,
    get_object_not_in_types,
)

IDF.setiddname("../resources/V9-5-0-Energy+.idd")


class SWH:
    """
    Add service water heating with OpenStudio ruby call
    """

    swh_settings = read_json("swh_settings.json")
    swh_dev_folder_name = swh_settings["swh_intermediate_folder_name"]
    considered_swh_fuel_types = swh_settings["considered_swh_fuel_types"]

    def __init__(self, case: Dict, idf: IDF):

        self.idf = idf
        self.case = case
        self.swh_fuel = self.case["swh"]["main_water_heater_fuel"]
        self.main_service_water_peak_flowrate = self.case["swh"][
            "main_service_water_peak_flowrate"
        ]
        self.code_version = self.case["code_version"]
        self.swh_efficiency = self.case["swh"]["main_water_heater_thermal_efficiency"]
        if (
            math.isnan(self.swh_efficiency)
            or (self.swh_efficiency < 0)
            or (self.swh_efficiency > 1)
        ):
            self.swh_efficiency = self.swh_settings[
                "main_water_heater_default_thermal_efficiency"
            ]
        self.pure_swh_objs = None
        self.exc_objs = None
        self.exc_obj_types = None
        self.replacing_schedules_refs = None

        if self.swh_fuel not in self.considered_swh_fuel_types:
            print(
                f"NO SWH IS ADDED because {self.swh_fuel} in not in the list of compatible swh fuel types \
                (Electricity, NaturalGas, HeatPump)"
            )
            return

        # run modeling strategy
        self.generate_osstd_input_idf()
        self.run_osstd_rubycall()
        self.clean_up_save_add_osstd_output()
        self.modify_schedule_refs()

    def generate_osstd_input_idf(self):
        exc_swh_meta = read_json(
            self.swh_settings["excluded_osstd_swh_obj_types_file_path"]
        )
        self.exc_obj_types = [ot.upper().strip() for ot in exc_swh_meta[self.swh_fuel]]

        zones_idf = IDF(StringIO(""))
        zones_idf_obj_types = [
            ot.upper().strip()
            for ot in self.swh_settings["idf_obj_types_for_osstd_use"]
        ]

        objs = []
        for obj_type in zones_idf_obj_types:
            objs.extend(list(self.idf.idfobjects[obj_type]))
            if obj_type not in self.exc_obj_types:
                self.exc_obj_types.append(obj_type)

        for obj in objs:
            zones_idf.copyidfobject(obj)

        zones_idf.saveas(
            f"../{self.swh_dev_folder_name}/zones_{self.case['building_name']}.idf"
        )

    def run_osstd_rubycall(self):
        ruby_run = [
            "ruby",
            "swh.rb",
            self.case["building_name"],
            self.swh_fuel,
            str(self.main_service_water_peak_flowrate),
            str(self.swh_efficiency),
            self.code_version,
        ]

        run_proc = subprocess.run(ruby_run, capture_output=True)
        print("\nSTDOUT:")
        print(run_proc.stdout.decode("utf-8"))
        print("\nSTDERR")
        print(run_proc.stderr.decode("utf-8"))
        osstd_swhadded = IDF(
            f"../{self.swh_dev_folder_name}/zones_swhadded_{self.case['building_name']}.idf"
        )
        print("SWH excluded object types:")
        print(self.exc_obj_types)
        self.pure_swh_objs = get_object_not_in_types(osstd_swhadded, self.exc_obj_types)
        self.exc_objs = get_object_by_types(osstd_swhadded, self.exc_obj_types)

    def clean_up_save_add_osstd_output(self):
        for obj in self.pure_swh_objs:
            for field in obj.__dict__["objls"]:
                if field == "key":
                    continue

                if " Thermal Zone" in str(obj[field]):
                    obj[field] = obj[field].replace(
                        " Thermal Zone", ""
                    )  # take out 'thermal zone' in names/refs

                if "Node" in str(obj[field]):
                    obj[field] = obj[field].replace(
                        "Node", "UrbanBEM SWH Node"
                    )  # Append Node and Node List name to avoid conflicts with other modules

        swh_pure = IDF(StringIO(""))
        for obj in self.pure_swh_objs:
            swh_pure.copyidfobject(obj)
        swh_pure.saveas(f"../{self.swh_dev_folder_name}/swh_pure.idf")

        exc_objs_idf = IDF(StringIO(""))
        for obj in self.exc_objs:
            exc_objs_idf.copyidfobject(obj)
        exc_objs_idf.saveas(f"../{self.swh_dev_folder_name}/exc_objs.idf")

        self.idf = copy_idf_objects(self.idf, swh_pure)

    def modify_schedule_refs(self):
        replace_osstd_schedules = read_json(
            self.swh_settings["replace_osstd_swh_schedules_refs_file_path"]
        )
        self.replacing_schedules_refs = replace_osstd_schedules[self.swh_fuel]

        # TODO: JXL this block is used in both swh and hvac, refactor to make it DRY
        for ref in self.replacing_schedules_refs:
            if ref["Obj_name"].strip() == "*":
                objs = self.idf.idfobjects[ref["Class"].upper().strip()]
            else:
                objs = []
                objs_pre = self.idf.idfobjects[ref["Class"].upper().strip()]
                for obj in objs_pre:
                    if obj["Name"].lower().strip() == ref["Obj_name"].lower().strip():
                        objs.append(obj)
                if len(objs) != 1:
                    print(f"ERROR: schedule ref for {ref} is not unique, please Check!")

            field_name = ref["Field"].replace(" ", "_").strip()
            field_value = ref["Sch_name"]
            batch_modify_idf_objs(objs, {field_name: field_value})

        self.idf.saveas(
            f"../{self.swh_dev_folder_name}/swh_final_{self.case['building_name']}.idf"
        )

    def save_idf(self, path):
        self.idf.saveas(path, lineendings="unix")


def main():
    testidf = IDF("../swh_dev/hvac_final_3306.idf")
    test_proc_case = {
        "building_name": "swhtest3306",
        "code_version": "90.1-2013",
        "swh": {
            "main_water_heater_fuel": "Electricity",
            "main_service_water_peak_flowrate": 6.30902e-5,  # m^3/s for 1 gal/min
        },
    }

    swh_obj = SWH(test_proc_case, testidf)
    swh_obj.save_idf("../swh_dev/swhadded.idf")


if __name__ == "__main__":
    main()
