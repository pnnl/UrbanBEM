from io import StringIO
from typing import Dict
from eppy import modeleditor
from eppy.modeleditor import IDF
from recipes import copy_idf_objects

IDF.setiddname("../resources/V9-5-0-Energy+.idd")


class EVCharger:
    def __init__(self, case: Dict, idf: IDF):
        
        self.idf = idf
        evflag = False
        
        if case["ev_charger"]["has_ev_charger"].lower() == "yes":
            evflag = True
            self.num_ev = case["ev_charger"]["num_ev_charger"]
            # 3.3kW per charger-EV
            self.charger_power = 3300
        
        self.add_ev_charger(
            has_ev_charger = evflag
        )

    def set_ev_charger_objects(self) -> IDF:
        """Set ev charger object: exterior:fuelequipment"""
        
        local_idf = IDF(StringIO(""))

        schedule_dict = {
                "key": "SCHEDULE:COMPACT",
                "Name": "EV Charger Schedule",
                "Schedule_Type_Limits_Name": "Fraction",
                "Field_1": "Through: 12/31",
                "Field_2": "For: Weekdays",
                "Field_3": "Until: 8:00",
                "Field_4": 0,
                "Field_5": "Until: 17:00",
                "Field_6": 1,
                "Field_7": "Until: 24:00",
                "Field_8": 0,
                "Field_9": "AllOtherDays",
                "Field_10": "Until: 8:00",
                "Field_11": 0,
                "Field_12": "Until: 17:00",
                "Field_13": 1,
                "Field_14": "Until: 24:00",
                "Field_15": 0,
            }
        
        local_idf.newidfobject(**schedule_dict)

        for i in range(self.num_ev):

            charger_dict = {
                "key": "EXTERIOR:FUELEQUIPMENT",
                "Name": "EV Charger " + str(i + 1),
                "Fuel_Use_Type": "Electricity",
                "Schedule_Name": "EV Charger Schedule",
                "Design_Level": self.charger_power,
                "EndUse_Subcategory": "EV",
            }

            local_idf.newidfobject(**charger_dict)

        return local_idf

    def add_ev_charger(self, has_ev_charger = False) -> IDF:
        """
        Set ev charger objects
        """
        if has_ev_charger:
            self.idf = copy_idf_objects(self.idf, self.set_ev_charger_objects())

        return self.idf
    
    
    def save_idf(self, path):
        self.idf.saveas(path, lineendings="unix")