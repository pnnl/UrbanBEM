from typing import Dict
import recipes
import adaptors


class Preprocessor:
    def __init__(self, case: Dict):
        self.case = case  # input case dict after unit version
        self.case_proc = {}  # output case dict placeholder
        self.keepkeys = [   # TODO: gradually reduce this list when building up the preprocessors
            "building_name",
            "building_area_type",
            "year_built",
            "ashrae_climate_zone",
            "epw_file",
            "gross_conditioned_area",
            "wall_type",
            "wall_u_factor",
            "roof_type",
            "roof_u_factor",
            "window_U_factor",
            "window_shgc",
            "people_density",
            "lpd",
            "plug_load_density",
            "Infiltration_rate",
            "weekly_occupied_hours(hr/wk)",
            "number_days_open_workday",
            "number_days_open_weekend",
            "heating_system_type",
            "cooling_system_type",
            "ventilation_rate",
            "economizer_used",
            "heat_recovery_used"
        ]
        self.keep_is()

        self.geometry_procudures()

    def geometry_procudures(self):  # general preprocess organizer
        self.populate_zone_geometry()

    def keep_is(self):  # case properties to be moved to final case directly
        for key in self.keepkeys:
            self.case_proc[key] = self.case[key]

    def populate_zone_geometry(self):
        # if self.case["data_source"] == "cbecs":
        #     self.case_proc["zone_geometry"] = adaptors.populate_cbecs_zones(self.case)
        # if self.case["data_source"] == "comcheck":
        #     self.case_proc["zone_geometry"] = adaptors.populate_comcheck_zones(
        #         self.case
        #     )
        self.case_proc['zone_geometry'] = adaptors.populate_std_zones(self.case)
