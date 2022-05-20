from io import StringIO
from typing import Dict, List
from eppy import modeleditor
from eppy.modeleditor import IDF
from recipes import copy_idf_objects, read_json


IDF.setiddname("../resources/V9-5-0-Energy+.idd")


class Schedule:
    """Convernt standard schedule info from json to IDF object and inject"""

    schedule_settings = read_json("schedule_settings.json")
    daytype_map = {
        value: key for key, value in schedule_settings["day_of_week_mappings"].items()
    }  # flip kv

    def __init__(self, case: Dict, idf: IDF):
        self.idf = idf
        self.schedules_dict = case["schedules"]
        self.set_schedules()

    def set_schedules(self):
        for key, val in self.schedules_dict.items():
            self.idf = copy_idf_objects(self.idf, self.sch_dict2idf(val))

    def sch_dict2idf(self, schedule_dict: Dict) -> IDF:
        """translate a multi-level dict of schedule to an Schedule:Compact idf object"""
        local_idf = IDF(StringIO(""))
        sch_kwargs = {
            "key": "SCHEDULE:COMPACT",
            "Name": schedule_dict["name"],
            "Schedule_Type_Limits_Name": schedule_dict["type"],
        }
        field_num = 0
        for p_key, period in schedule_dict["periods"].items():
            field_num += 1
            sch_kwargs[f"Field_{int(field_num)}"] = f"Through: {period['through']}"
            for dow, hourly_list in period["day_of_week"].items():
                tuple_list = self.get_schedule_val_changes(hourly_list)
                field_num += 1
                sch_kwargs[f"Field_{int(field_num)}"] = f"For: {self.daytype_map[dow]}"
                for dual in tuple_list:
                    field_num += 1
                    sch_kwargs[f"Field_{int(field_num)}"] = dual[0]
                    field_num += 1
                    sch_kwargs[f"Field_{int(field_num)}"] = dual[1]

        schedule = local_idf.newidfobject(**sch_kwargs)

        return local_idf

    def get_schedule_val_changes(self, hourlyList: List[float]) -> List[tuple]:
        """check a 24 hour schedule value and return list of tuple (changing hour, changed value)

        e.g. ("Until: 19:00", "23.9")
        """

        # data validation
        if len(hourlyList) != 24:
            print("ERROR: schedule value is not a 24 hour vector")
            return None

        change_tuple_list = []
        for i in range(1, 24):
            if hourlyList[i] == hourlyList[i - 1]:
                continue
            change_tuple_list.append((f"Until: {int(i)}:00", hourlyList[i - 1]))
        change_tuple_list.append((f"Until: {int(24)}:00", hourlyList[23]))

        return change_tuple_list

    def save_idf(self, path):
        self.idf.saveas(path, lineendings="unix")
