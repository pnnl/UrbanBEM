from io import StringIO
from typing import Dict, List
import json
import pandas as pd
from geomeppy import IDF

from recipes import read_json, copy_idf_objects

IDF.setiddname("../resources/V9-5-0-Energy+.idd")


class Outputs:
    """Process Output related objects in IDF
    """

    output_settings = read_json("output_settings.json")
    delete_variables = output_settings["delete_all_variables"]
    meters_tobeadded = output_settings["reporting_meters"]

    def __init__(self, case: Dict, idf: IDF):
        self.idf = idf
        self.case = case

        self.delete_existing_variables()
        self.add_meters()

    def delete_existing_variables(self):
        if not self.delete_variables:
            return

        var_objs = list(
            self.idf.idfobjects["Output:Variable".upper()]
        )  # cast into list, otherwise it is a reference to objs and will change dynamically during looping
        if len(var_objs) == 0:
            print("Intend to delete all existing output variables, but none found.")
            return
        print(f"Delete {len(var_objs)} existing Output:Variable objects")
        for obj in var_objs:
            self.idf.removeidfobject(obj)
        return

    def add_meters(self):
        for meter in self.meters_tobeadded:
            meter["key"] = "OUTPUT:METER"
            self.idf.newidfobject(**meter)

    def save_idf(self, path):
        self.idf.saveas(path, lineendings="unix")


def main():

    testidf = IDF("../devoutput/hvac_added.idf")
    test_proc_case = (
        {}
    )  # this processor does not really need info from case, but just keep for consistency for now.

    hvacadded_obj = Outputs(test_proc_case, testidf)
    hvacadded_obj.save_idf("../devoutput/outputsadded.idf")


if __name__ == "__main__":
    main()
