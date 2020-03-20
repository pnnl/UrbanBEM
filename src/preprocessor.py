from typing import Dict
import recipes
import adaptors


class Preprocessor:
    def __init__(self, case: Dict):
        self.case = case  # input case dict after unit version
        self.case_proc = {}  # output case dict placeholder
        self.keepkeys = ["building_name", "data_source", "building_area_type"]
        self.keep_is()

        self.geometry_procudures()

    def geometry_procudures(self):  # general preprocess organizer
        self.populate_zone_geometry()

    def keep_is(self):  # case properties to be moved to final case directly
        for key in self.keepkeys:
            self.case_proc[key] = self.case[key]

    def populate_zone_geometry(self):
        if self.case["data_source"] == "cbecs":
            self.case_proc["zone_geometry"] = adaptors.populate_cbecs_zones(self.case)
        if self.case["data_source"] == "comcheck":
            self.case_proc["zone_geometry"] = adaptors.populate_comcheck_zones(
                self.case
            )
