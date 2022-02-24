from typing import Dict, List
from eppy import modeleditor
from eppy.modeleditor import IDF
from recipes import copy_idf_objects
import datetime
import pandas as pd
import schedule_preparation as sp
from randomizeDayVector import randomizeDayVector
import os

IDF.setiddname("../resources/Energy+V9_5_0.idd")

class Schedule:
    """Convert standard schedule info from json to IDF object and inject"""

    def __init__(self, case: Dict, idf: IDF, randomizeHours: bool, randomizeValues: bool):
        self.idf = idf
        self.schedules_dict = case["schedules"]
        self.building_name = case["building_name"]
        self.generate_schedules(case, randomizeHours, randomizeValues)
        self.set_schedules()

    # Randomizes certain schedules and saves the hour-by-hour values for the year in a csv
    def generate_schedules(self, case, randomizeHours, randomizeValues):

        scheduleDF = pd.DataFrame(
            columns = [
                'bldg_occ_sch', 
                'bldg_light_sch',
                'bldg_hvac_operation_sch',
                'bldg_electric_equipment_sch',
                'bldg_clg_setp_sch',
                'bldg_htg_setp_sch',
                'bldg_infiltration_sch',
                'activity_sch',
                'always_on'
            ]
        )

        currentDate = datetime.date(year = 2019, month = 1, day = 1)

        while currentDate <= datetime.date(year = 2019, month = 12, day = 31):

            weekdayKey = 'Sat' if currentDate.weekday() == 5 else 'Sun' if currentDate.weekday() == 6 else 'WD'

            bldg_business_hour_dict, consider_lunch_time = sp.bldg_business_hour(case, randomizeHours)
            bldg_occ_sch_dict = sp.bldg_occ_sch(bldg_business_hour_dict, consider_lunch_time)
            bldg_hvac_operation_sch = sp.bldg_hvac_operation_sch(bldg_business_hour_dict, consider_lunch_time)

            daySchedules = {}
            daySchedules['bldg_occ_sch'] = bldg_occ_sch_dict[weekdayKey]
            daySchedules['bldg_light_sch'] = sp.bldg_light_sch(bldg_business_hour_dict, consider_lunch_time)[weekdayKey]
            daySchedules['bldg_hvac_operation_sch'] = bldg_hvac_operation_sch[weekdayKey]
            daySchedules['bldg_electric_equipment_sch'] = sp.bldg_electric_equipment_sch(bldg_occ_sch_dict)[weekdayKey]
            daySchedules['bldg_clg_setp_sch'] = sp.bldg_clg_setp_sch(bldg_hvac_operation_sch)[weekdayKey]
            daySchedules['bldg_htg_setp_sch'] = sp.bldg_htg_setp_sch(bldg_hvac_operation_sch)[weekdayKey]
            daySchedules['bldg_infiltration_sch'] = sp.bldg_infiltration_sch(bldg_hvac_operation_sch)[weekdayKey]
            daySchedules['activity_sch'] = sp.activity_sch()[weekdayKey]
            daySchedules['always_on'] = sp.always_on()[weekdayKey]

            if randomizeValues:
                daySchedules['bldg_occ_sch'] = randomizeDayVector(daySchedules['bldg_occ_sch'])
                daySchedules['bldg_light_sch'] = randomizeDayVector(daySchedules['bldg_light_sch'])
                daySchedules['bldg_electric_equipment_sch'] = randomizeDayVector(daySchedules['bldg_electric_equipment_sch'])

            scheduleDF = scheduleDF.append(pd.DataFrame(daySchedules), ignore_index = True)

            currentDate += datetime.timedelta(days = 1)


        # Rename the index
        scheduleDF.index.name = 'timestamp'

        # Create schedules directory, if it doesn't exist
        if not os.path.exists('../input/schedules'):
            os.makedirs('../input/schedules')

        # Save the dataframe to a CSV
        scheduleDF.to_csv(f'../input/schedules/{self.building_name}_schedules.csv')

    
    # Set the SCHEDULE:FILE objects in the IDF
    def set_schedules(self):
            
        filename = f'../input/schedules/{self.building_name}_schedules.csv'
        scheduleDF = pd.read_csv(filename, index_col = 'timestamp')

        for scheduleName in scheduleDF.columns:

            sch_kwargs = {
                'key': 'SCHEDULE:FILE',
                'Schedule_Type_Limits_Name': 'Any Number',
                'Name': scheduleName, 
                'File_Name': os.getcwd().replace('/src', filename.strip('.')),
                'Column_Number': scheduleDF.columns.get_loc(scheduleName) + 2,
                'Rows_to_Skip_at_Top': 1,
                'Number_of_Hours_of_Data': 8760,
                'Column_Separator': 'Comma',
                'Interpolate_to_Timestep': 'No'
            }

            self.idf.newidfobject(**sch_kwargs)
            
    def save_idf(self, path):
        self.idf.saveas(path, lineendings="unix")
