from typing import Dict, List
from eppy import modeleditor
from eppy.modeleditor import IDF
from recipes import copy_idf_objects, get_schedule_by_name
import datetime
import pandas as pd
import schedule_preparation as sp
from randomizeDayVector import randomizeDayVector
import os

IDF.setiddname("../resources/V9-5-0-Energy+.idd")


class Schedule:
    """Convert standard schedule info from json to IDF object and inject"""

    def __init__(
        self, case: Dict, idf: IDF, randomizeHours: bool, randomizeValues: bool
    ):
        self.idf = idf
        self.schedules_dict = case["schedules"]
        self.building_name = case["building_name"]
        self.generate_schedules(case, randomizeHours, randomizeValues)
        self.set_schedules()

    # Randomizes certain schedules and saves the hour-by-hour values for the year in a csv
    def generate_schedules(self, case, randomizeHours, randomizeValues):

        scheduleDF = pd.DataFrame(
            columns=[x[1]["name"] for x in self.schedules_dict.items()]
        )

        ns_upperbound = 0.1
        if case['building_area_type'].strip().lower() in ['health-care clinic', 'hospital']:
            ns_upperbound = 0.2

        currentDate = datetime.date(year=2019, month=1, day=1)

        while currentDate <= datetime.date(year=2019, month=12, day=31):

            weekdayKey = (
                "Sat"
                if currentDate.weekday() == 5
                else "Sun"
                if currentDate.weekday() == 6
                else "WD"
            )

            bldg_business_hour_dict, consider_lunch_time = sp.bldg_business_hour(
                case, randomizeHours
            )
            bldg_occ_sch_dict = sp.bldg_occ_sch(
                bldg_business_hour_dict, consider_lunch_time
            )
            bldg_swh_use_sch_dict = sp.schdule_dict_multiplier(
                sp.bldg_occ_sch(bldg_business_hour_dict, False), multiplier=0.1
            )
            bldg_hvac_operation_sch = sp.bldg_hvac_operation_sch(
                bldg_business_hour_dict, consider_lunch_time
            )

            # TODO: JXL method calls below need to be replaced because processed inputs have been added to case dict

            daySchedules = {}
            daySchedules["bldg_occ_sch"] = bldg_occ_sch_dict[weekdayKey]
            daySchedules["bldg_swh_use_sch"] = bldg_swh_use_sch_dict[weekdayKey]
            daySchedules["bldg_light_sch"] = sp.sch_night_squeeze(
                sp.bldg_light_sch(bldg_business_hour_dict, overall_sch_factor=0.1),
                upperbound=ns_upperbound,
            )[weekdayKey]
            daySchedules["bldg_ext_light_sch"] = sp.bldg_light_sch(
                bldg_business_hour_dict, overall_sch_factor=1
            )[
                weekdayKey
            ]  # TODO: to be replaced with ext light specific method
            daySchedules["bldg_hvac_operation_sch"] = bldg_hvac_operation_sch[
                weekdayKey
            ]
            daySchedules["bldg_electric_equipment_sch"] = sp.sch_night_squeeze(
                sp.bldg_electric_equipment_sch(bldg_occ_sch_dict), upperbound=ns_upperbound
            )[weekdayKey]
            daySchedules["bldg_gas_equipment_sch"] = sp.sch_night_squeeze(
                sp.bldg_electric_equipment_sch(bldg_occ_sch_dict), upperbound=ns_upperbound
            )[
                weekdayKey
            ]  # TODO: to be replaced with gas specific method
            daySchedules["bldg_clg_setp_sch"] = get_schedule_by_name(
                case["schedules"], "bldg_clg_setp_sch"
            )[weekdayKey]
            daySchedules["bldg_htg_setp_sch"] = get_schedule_by_name(
                case["schedules"], "bldg_htg_setp_sch"
            )[weekdayKey]
            daySchedules["bldg_infiltration_sch"] = sp.bldg_infiltration_sch(
                bldg_hvac_operation_sch
            )[weekdayKey]
            daySchedules["bldg_door_infiltration_sch"] = sp.bldg_infiltration_sch(
                bldg_hvac_operation_sch
            )[
                weekdayKey
            ]  # TODO: to be replaced with door infiltration specific method
            daySchedules["activity_sch"] = sp.activity_sch()[weekdayKey]
            daySchedules["always_on"] = sp.always_on()[weekdayKey]

            if randomizeValues:
                daySchedules["bldg_occ_sch"] = randomizeDayVector(
                    daySchedules["bldg_occ_sch"]
                )
                daySchedules["bldg_swh_use_sch"] = randomizeDayVector(
                    daySchedules["bldg_swh_use_sch"]
                )
                daySchedules["bldg_light_sch"] = randomizeDayVector(
                    daySchedules["bldg_light_sch"]
                )
                daySchedules["bldg_electric_equipment_sch"] = randomizeDayVector(
                    daySchedules["bldg_electric_equipment_sch"]
                )
                daySchedules["bldg_gas_equipment_sch"] = randomizeDayVector(
                    daySchedules["bldg_gas_equipment_sch"]
                )

            scheduleDF = scheduleDF.append(
                pd.DataFrame(daySchedules), ignore_index=True
            )

            currentDate += datetime.timedelta(days=1)

        # Rename the index
        scheduleDF.index.name = "timestamp"

        # Create schedules directory, if it doesn't exist
        if not os.path.exists("../input/schedules"):
            os.makedirs("../input/schedules")

        # Save the dataframe to a CSV
        scheduleDF.to_csv(f"../input/schedules/{self.building_name}_schedules.csv")

    # Set the SCHEDULE:FILE objects in the IDF
    def set_schedules(self):

        filename = f"../input/schedules/{self.building_name}_schedules.csv"
        scheduleDF = pd.read_csv(filename, index_col="timestamp")

        for scheduleName in scheduleDF.columns:

            sch_kwargs = {
                "key": "SCHEDULE:FILE",
                "Schedule_Type_Limits_Name": "Any Number",
                "Name": scheduleName,
                "File_Name": os.getcwd().replace("/src", filename.strip(".")),
                "Column_Number": scheduleDF.columns.get_loc(scheduleName) + 2,
                "Rows_to_Skip_at_Top": 1,
                "Number_of_Hours_of_Data": 8760,
                "Column_Separator": "Comma",
                "Interpolate_to_Timestep": "No",
            }

            self.idf.newidfobject(**sch_kwargs)

    def save_idf(self, path):
        self.idf.saveas(path, lineendings="unix")
