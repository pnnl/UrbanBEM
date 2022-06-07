import math
from typing import Dict
import json
import numpy as np

# bldg_business_hour
def bldg_business_hour(case: Dict, randomizeHours: bool) -> Dict:
    f = open("./schedule_database.json")
    schedule_database = json.load(f)

    center_operation_hour_wd = int(
        schedule_database[case["building_area_type"]]["Center Operation Hour (WD)"]
    )
    center_operation_hour_others = int(
        schedule_database[case["building_area_type"]]["Center Operation Hour (Others)"]
    )
    ratio_wd_all = float(
        schedule_database[case["building_area_type"]]["Ratio of WD/All"]
    )
    consider_lunch_time = schedule_database[case["building_area_type"]][
        "consider_lunch_time"
    ]

    weekly_occupied_hours = case["weekly_occupied_hours"]
    number_days_open_workday = case["number_days_open_workday"]
    number_days_open_weekend = case["number_days_open_weekend"]

    if randomizeHours:

        center_operation_hour_wd = round(np.random.normal(center_operation_hour_wd, 1))
        center_operation_hour_wd = (
            1
            if center_operation_hour_wd < 1
            else 24
            if center_operation_hour_wd > 24
            else center_operation_hour_wd
        )

        center_operation_hour_others = round(
            np.random.normal(center_operation_hour_others, 1)
        )
        center_operation_hour_others = (
            1
            if center_operation_hour_others < 1
            else 24
            if center_operation_hour_others > 24
            else center_operation_hour_others
        )

        # ratio_wd_all = np.random.normal(ratio_wd_all, 0.02)
        # ratio_wd_all = 0 if ratio_wd_all < 0 else 1 if ratio_wd_all > 1 else ratio_wd_all

        weekly_occupied_hours = round(
            np.random.normal(weekly_occupied_hours, 0.05 * weekly_occupied_hours)
        )
        weekly_occupied_hours = (
            0
            if weekly_occupied_hours < 0
            else 168
            if weekly_occupied_hours > 168
            else weekly_occupied_hours
        )

        # number_days_open_workday = round(np.random.normal(number_days_open_workday, 0.5))
        # number_days_open_workday = 0 if number_days_open_workday < 0 else 5 if number_days_open_workday > 5 else number_days_open_workday

        # number_days_open_weekend = round(np.random.normal(number_days_open_weekend, 0.5))
        # number_days_open_weekend = 0 if number_days_open_weekend < 0 else 2 if number_days_open_weekend > 2 else number_days_open_weekend

    if number_days_open_weekend == 0:
        WD_hour = round(weekly_occupied_hours / number_days_open_workday)
        Sat_Sun_hour = 0
    else:
        WD_hour = round(
            (weekly_occupied_hours * ratio_wd_all) / number_days_open_workday
        )
        Sat_Sun_hour = round(
            (weekly_occupied_hours * (1 - ratio_wd_all)) / number_days_open_workday
        )

    if WD_hour > 0:
        if round(center_operation_hour_wd - WD_hour / 2.0) < 0:
            start_hour_WD = 24 + round(center_operation_hour_wd - WD_hour / 2.0)
        else:
            start_hour_WD = round(center_operation_hour_wd - WD_hour / 2.0)
        if round(center_operation_hour_wd + WD_hour / 2.0) > 24:
            end_hour_WD = round(center_operation_hour_wd + WD_hour / 2.0) - 24
        else:
            end_hour_WD = round(center_operation_hour_wd + WD_hour / 2.0)

    if Sat_Sun_hour > 0:
        if round(center_operation_hour_others - Sat_Sun_hour / 2.0) < 0:
            start_hour_Sat_Sun = 24 + round(
                center_operation_hour_others - Sat_Sun_hour / 2.0
            )
        else:
            start_hour_Sat_Sun = round(center_operation_hour_others - WD_hour / 2.0)
        if round(center_operation_hour_others + Sat_Sun_hour / 2.0) > 24:
            end_hour_Sat_Sun = (
                round(center_operation_hour_others + Sat_Sun_hour / 2.0) - 24
            )
        else:
            end_hour_Sat_Sun = round(center_operation_hour_others + Sat_Sun_hour / 2.0)

    WD = []
    if start_hour_WD >= end_hour_WD:
        for i in range(end_hour_WD):
            WD.append(1)
        for i in range(end_hour_WD, start_hour_WD):
            WD.append(0)
        for i in range(start_hour_WD, 24):
            WD.append(1)
    else:
        for i in range(start_hour_WD):
            WD.append(0)
        for i in range(start_hour_WD, end_hour_WD):
            WD.append(1)
        for i in range(end_hour_WD, 24):
            WD.append(0)

    Sat_Sun = []
    if Sat_Sun_hour > 0:
        if start_hour_Sat_Sun >= end_hour_Sat_Sun:
            for i in range(end_hour_Sat_Sun):
                Sat_Sun.append(1)
            for i in range(end_hour_Sat_Sun, start_hour_Sat_Sun):
                Sat_Sun.append(0)
            for i in range(start_hour_Sat_Sun, 24):
                Sat_Sun.append(1)
        else:
            for i in range(start_hour_Sat_Sun):
                Sat_Sun.append(0)
            for i in range(start_hour_Sat_Sun, end_hour_Sat_Sun):
                Sat_Sun.append(1)
            for i in range(end_hour_Sat_Sun, 24):
                Sat_Sun.append(0)
    else:
        for i in range(24):
            Sat_Sun.append(0)

    bldg_business_hour_dict = {}

    for x in ["WD", "Sat", "Sun", "Hol", "Others"]:
        if x == "WD":
            bldg_business_hour_dict[x] = WD
        else:
            bldg_business_hour_dict[x] = Sat_Sun

    return bldg_business_hour_dict, consider_lunch_time


# bldg_occ_sch
def bldg_occ_sch(bldg_business_hour_dict: Dict, consider_lunch_time: str) -> Dict:
    bldg_occ_sch_dict = {}
    bldg_occ_sch_dict["WinDD"] = [0] * 24
    bldg_occ_sch_dict["SumDD"] = [1] * 24
    for key in bldg_business_hour_dict:
        hourly_sch = []
        for i in range(24):
            if (
                i == 12
                and consider_lunch_time == "Yes"
                and bldg_business_hour_dict[key][12] == 1
            ):
                hourly_sch.append(0.5)
            elif bldg_business_hour_dict[key][i] == 1:
                hourly_sch.append(0.95)
            elif (
                i == 0
                and bldg_business_hour_dict[key][0] == 0
                and bldg_business_hour_dict[key][23] == 1
            ):
                hourly_sch.append(0.2)
            elif (
                i == 23
                and bldg_business_hour_dict[key][23] == 0
                and bldg_business_hour_dict[key][0] == 1
            ):
                hourly_sch.append(0.2)
            elif (
                i > 0
                and i < 23
                and bldg_business_hour_dict[key][i] == 0
                and (
                    bldg_business_hour_dict[key][i - 1] == 1
                    or bldg_business_hour_dict[key][i + 1] == 1
                )
            ):
                hourly_sch.append(0.2)
            else:
                hourly_sch.append(0)
        bldg_occ_sch_dict[key] = hourly_sch

    return bldg_occ_sch_dict


# bldg_electric_equipment_sch
def bldg_electric_equipment_sch(bldg_occ_sch_dict: Dict) -> Dict:
    bldg_electric_equipment_sch_dict = {}
    bldg_electric_equipment_sch_dict["WinDD"] = [0] * 24
    bldg_electric_equipment_sch_dict["SumDD"] = [1] * 24
    for key in bldg_occ_sch_dict:
        if key != "WinDD" and key != "SumDD":
            hourly_sch = []
            for i in range(24):
                hourly_sch.append(0.1 + bldg_occ_sch_dict[key][i] * 0.9)
            bldg_electric_equipment_sch_dict[key] = hourly_sch

    return bldg_electric_equipment_sch_dict


# bldg_light_sch
def bldg_light_sch(bldg_business_hour_dict: Dict, consider_lunch_time: str) -> Dict:
    bldg_light_sch_dict = {}
    bldg_light_sch_dict["WinDD"] = [0] * 24
    bldg_light_sch_dict["SumDD"] = [1] * 24
    for key in bldg_business_hour_dict:
        hourly_sch = []
        for i in range(24):
            if bldg_business_hour_dict[key][i] == 1:
                hourly_sch.append(0.9)
            elif (
                i == 0
                and bldg_business_hour_dict[key][0] == 0
                and bldg_business_hour_dict[key][23] == 1
            ):
                hourly_sch.append(0.3)
            elif (
                i == 23
                and bldg_business_hour_dict[key][23] == 0
                and bldg_business_hour_dict[key][0] == 1
            ):
                hourly_sch.append(0.3)
            elif (
                i > 0
                and i < 23
                and bldg_business_hour_dict[key][i] == 0
                and (
                    bldg_business_hour_dict[key][i - 1] == 1
                    or bldg_business_hour_dict[key][i + 1] == 1
                )
            ):
                hourly_sch.append(0.3)
            else:
                hourly_sch.append(0.05)
        bldg_light_sch_dict[key] = hourly_sch

    return bldg_light_sch_dict


# bldg_hvac_operation_sch
def bldg_hvac_operation_sch(
    bldg_business_hour_dict: Dict, consider_lunch_time: str
) -> Dict:
    bldg_hvac_operation_sch_dict = {}
    sumdd_windd_hourly_sch = []
    for i in range(24):
        if bldg_business_hour_dict["Sun"][i] == 1:
            sumdd_windd_hourly_sch.append(1)
        elif (
            i == 23
            and bldg_business_hour_dict["Sun"][23] == 0
            and bldg_business_hour_dict["Sun"][0] == 1
        ):
            sumdd_windd_hourly_sch.append(1)
        elif (
            i < 23
            and bldg_business_hour_dict["Sun"][i] == 0
            and bldg_business_hour_dict["Sun"][i + 1] == 1
        ):
            sumdd_windd_hourly_sch.append(1)
        else:
            sumdd_windd_hourly_sch.append(0)
    bldg_hvac_operation_sch_dict["WinDD"] = sumdd_windd_hourly_sch
    bldg_hvac_operation_sch_dict["SumDD"] = sumdd_windd_hourly_sch

    for key in bldg_business_hour_dict:
        hourly_sch = []
        for i in range(24):
            if bldg_business_hour_dict[key][i] == 1:
                hourly_sch.append(1)
            elif (
                i == 23
                and bldg_business_hour_dict[key][23] == 0
                and bldg_business_hour_dict[key][0] == 1
            ):
                hourly_sch.append(1)
            elif (
                i < 23
                and bldg_business_hour_dict[key][i] == 0
                and bldg_business_hour_dict[key][i + 1] == 1
            ):
                hourly_sch.append(1)
            else:
                hourly_sch.append(0)
        bldg_hvac_operation_sch_dict[key] = hourly_sch

    return bldg_hvac_operation_sch_dict


# bldg_clg_setp_sch
def bldg_clg_setp_sch(bldg_hvac_operation_sch_dict: Dict, case: Dict) -> Dict:
    occ_sp = 24
    unocc_sp = 26.7
    if "temp_setpoint_cool" in case.keys():
        if not math.isnan(case["temp_setpoint_cool"]):
            occ_sp = case["temp_setpoint_cool"]
    if "temp_setpoint_cool_unoccupied" in case.keys():
        if not math.isnan(case["temp_setpoint_cool_unoccupied"]):
            unocc_sp = case["temp_setpoint_cool_unoccupied"]
    bldg_clg_setp_sch_dict = {}
    for key in bldg_hvac_operation_sch_dict:
        hourly_sch = []
        for i in range(24):
            if bldg_hvac_operation_sch_dict[key][i] == 1:
                hourly_sch.append(occ_sp)
            else:
                hourly_sch.append(unocc_sp)
        bldg_clg_setp_sch_dict[key] = hourly_sch

    return bldg_clg_setp_sch_dict


# bldg_htg_setp_sch
def bldg_htg_setp_sch(bldg_hvac_operation_sch_dict: Dict, case: Dict) -> Dict:
    occ_sp = 21
    unocc_sp = 15.6
    if "temp_setpoint_heat" in case.keys():
        if not math.isnan(case["temp_setpoint_heat"]):
            occ_sp = case["temp_setpoint_heat"]
    if "temp_setpoint_heat_unoccupied" in case.keys():
        if not math.isnan(case["temp_setpoint_heat_unoccupied"]):
            unocc_sp = case["temp_setpoint_heat_unoccupied"]
    bldg_htg_setp_sch_dict = {}
    for key in bldg_hvac_operation_sch_dict:
        hourly_sch = []
        for i in range(24):
            if bldg_hvac_operation_sch_dict[key][i] == 1:
                hourly_sch.append(occ_sp)
            else:
                hourly_sch.append(unocc_sp)
        bldg_htg_setp_sch_dict[key] = hourly_sch

    return bldg_htg_setp_sch_dict


# bldg_infiltration_sch
def bldg_infiltration_sch(bldg_hvac_operation_sch_dict: Dict) -> Dict:
    bldg_infiltration_sch_dict = {}
    for key in bldg_hvac_operation_sch_dict:
        hourly_sch = []
        for i in range(24):
            if bldg_hvac_operation_sch_dict[key][i] == 1:
                hourly_sch.append(0.25)
            else:
                hourly_sch.append(1)
        bldg_infiltration_sch_dict[key] = hourly_sch

    return bldg_infiltration_sch_dict


# activity_sch
def activity_sch():
    activity_sch_dict = {}
    for x in ["WinDD", "SumDD", "WD", "Sat", "Sun", "Hol", "Others"]:
        activity_sch_dict[x] = [120] * 24

    return activity_sch_dict


# always_on
def always_on():
    always_on_dict = {}
    for x in ["WinDD", "SumDD", "WD", "Sat", "Sun", "Hol", "Others"]:
        always_on_dict[x] = [1] * 24

    return always_on_dict


# schedule multiplier
def schdule_dict_multiplier(sch_dict, multiplier):
    new_sch_dict = {}
    for k, v in sch_dict.items():
        new_sch_dict[k] = [elem * multiplier for elem in v]
    return new_sch_dict
