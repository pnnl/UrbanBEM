from typing import Dict
import recipes
import adaptors


class Preprocessor:
    def __init__(self, case: Dict):
        self.case = case  # input case dict after unit version
        self.case_proc = {}  # output case dict placeholder
        self.keepkeys = [  # gradually reduce this list when building up the preprocessors
            "building_name",
            "building_area_type",
            "year_built",
            "ashrae_climate_zone",
            "epw_file",
            "gross_conditioned_area",
            "heating_system_type",
            "cooling_system_type",
            "ventilation_rate",
            "economizer_used",
            "heat_recovery_used",
        ]
        self.keep_is()

        self.geometry_procedures()
        self.construction_procedures()
        self.schedule_procedures()
        self.loads_procedures()

    def geometry_procedures(self):  # general preprocess organizer
        self.populate_zone_geometry()

    def construction_procedures(self):
        self.populate_constructions()
        self.groundtemp_profile()

    def schedule_procedures(self):
        self.populate_hourly_schedules()

    def loads_procedures(self):
        self.populate_loads()

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
        self.case_proc["zone_geometry"] = adaptors.populate_std_zones(self.case)

    def populate_hourly_schedules(self):
        self.case_proc["schedules"] = adaptors.populate_std_schedules(self.case)

    def populate_loads(self):
        self.case_proc["internal_loads"] = adaptors.populate_std_loads(self.case)

    def populate_constructions(self):
        self.case_proc["constructions"] = adaptors.populate_std_constructions(self.case)

    def groundtemp_profile(self):
        self.case_proc["constructions"][
            "ground_temp_profile_jan2dec"
        ] = adaptors.populate_std_ground_temp_jan2dec(self.case)
