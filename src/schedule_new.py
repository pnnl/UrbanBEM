from typing import Dict, List
from eppy import modeleditor
from eppy.modeleditor import IDF
from recipes import copy_idf_objects
import datetime
import pandas as pd
from itertools import chain
from randomizeDayVector import randomizeDayVector
import os

IDF.setiddname("../resources/Energy+V9_0_1.idd")

class Schedule:
    """Convert standard schedule info from json to IDF object and inject"""

    def __init__(self, case: Dict, idf: IDF, randomize: bool):
        self.idf = idf
        self.schedules_dict = case["schedules"]
        self.building_name = case["building_name"]
        self.generate_schedules(randomize)
        self.set_schedules()

    # Randomizes certain schedules and saves the hour-by-hour values for the year in a csv
    def generate_schedules(self, randomize):
        
        # Create a dataframe to hold unrandomized and randomized hour-by-hour schedule values, for all schedules, over a year
        scheduleDF = pd.DataFrame()

        with open('../input/processed_inputs/cbecs1_processed.json', 'r') as file:

            # Convert each schedule into a (sometimes) randomized vector giving the value of the schedule for each hour over a year
            for schedule in self.schedules_dict.values():

                # Initialize the output vector and a date object used to iterate through the year
                outputVector = []
                currentDate = datetime.date(year = 2019, month = 1, day = 1)

                # Build up the vector period-by-period (e.g. 'through: 12/31' would result in one loop)
                for period in schedule['periods'].values():

                    # Get end date of period
                    endMonth, endDay = [int(n) for n in period['through'].split('/')]

                    # Build up the vector day-by-day until the end of the period
                    while currentDate <= datetime.date(year = 2019, month = endMonth, day = endDay):

                        # Choose the appropriate 24-hour vector based on the day of the week (Saturday, Sunday, or Weekday)
                        dayVector = period['day_of_week']['Sat'] if currentDate.weekday() == 5 else period['day_of_week']['Sun'] if currentDate.weekday() == 6 else period['day_of_week']['WD']

                        # Randomize the day vector, unless it is boolean, and add it to the randomized output vector
                        randomized = ['bldg_occ_sch', 'bldg_electric_equipment_sch', 'bldg_light_sch']
                        outputVector += dayVector if schedule['name'] not in randomized or not randomize else randomizeDayVector(dayVector, limit_step = False, squeeze = False)

                        # Increment the current day by 1
                        currentDate += datetime.timedelta(days = 1)

                    # Add the vector to the dataframe
                    scheduleDF[schedule['name']] = outputVector

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
                'Schedule_Type_Limits_Name': '',
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
