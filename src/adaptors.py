""" Data transformers and wrappers"""
import math
from typing import Dict, List
from recipes import read_json
import pandas as pd
import schedule_preparation as sp

geometry_settings = read_json("geometry_settings.json")
orient_list = geometry_settings["orient_list"]


def populate_std_zones(case: Dict) -> Dict:
    """populate standard input zone geometry information

    The logic of populating standard input zone geometry roughly follows the geometry rules for comcheck inputs
    """

    building_area_type = case["building_area_type"]
    num_floors = case["number_of_floor"]
    conditioned_floor_area = case["gross_conditioned_area"] / num_floors
    height = case["floor_to_ceil_height"]
    perimeter_spec_dict = {
        "south": {
            "gross_wall_area": case["south_gross_wall_area"] / num_floors,
            "window_area": case["south_window_area"] / num_floors,
        },
        "west": {
            "gross_wall_area": case["west_gross_wall_area"] / num_floors,
            "window_area": case["west_window_area"] / num_floors,
        },
        "north": {
            "gross_wall_area": case["north_gross_wall_area"] / num_floors,
            "window_area": case["north_window_area"] / num_floors,
        },
        "east": {
            "gross_wall_area": case["east_gross_wall_area"] / num_floors,
            "window_area": case["east_window_area"] / num_floors,
        },
    }

    perimeter_spec_df = pd.DataFrame(perimeter_spec_dict).transpose()
    gross_wall_area = perimeter_spec_df["gross_wall_area"].sum()
    floor2wall_ratio = conditioned_floor_area / gross_wall_area

    init_thermalzone_df = pd.DataFrame()

    # add perimeter thermal zones spec
    for side in orient_list:
        spec_dict = perimeter_spec_dict[side]
        init_thermalzone_df = init_thermalzone_df.append(
            get_perimeter_row_dict(
                building_area_type,
                side,
                spec_dict["gross_wall_area"],
                floor2wall_ratio,
                height,
                spec_dict["window_area"],
                num_floors,
            ),
            ignore_index=True,
        )

    # add core zone spec if needed
    if floor2wall_ratio > 1.25:
        perimeter_area_sum = init_thermalzone_df["area"].sum()
        init_thermalzone_df = init_thermalzone_df.append(
            get_core_row_dict(
                building_area_type,
                conditioned_floor_area,
                perimeter_area_sum,
                height,
                num_floors,
            ),
            ignore_index=True,
        )

    init_thermalzone_dict = init_thermalzone_df.to_dict(orient="index")
    return init_thermalzone_dict


def get_perimeter_row_dict(
    bldg_area_type,
    side,
    gross_wall_area_perimeter,
    floor2wall_ratio,
    height,
    window_area_perimeter,
    num_floors=1,
):
    """helper to compute perimeter thermal zone dict spec"""
    row_dict = {}
    row_dict["name"] = f"{bldg_area_type}_{side}_zone"
    row_dict["type"] = "perimeter"
    row_dict["side"] = side
    row_dict["area"] = gross_wall_area_perimeter * min(floor2wall_ratio, 1.25)
    row_dict["height"] = height
    row_dict["length"] = gross_wall_area_perimeter / row_dict["height"]
    row_dict["depth"] = row_dict["area"] / row_dict["length"]
    row_dict["window_height"] = math.sqrt(
        window_area_perimeter / (row_dict["length"] / row_dict["height"])
    )
    row_dict["window_lengh"] = window_area_perimeter / row_dict["window_height"]
    row_dict["wwr"] = window_area_perimeter / gross_wall_area_perimeter
    row_dict["num_floors"] = num_floors
    return row_dict


def get_core_row_dict(
    bldg_area_type, conditioned_floor_area, perimeter_area_sum, height, num_floors=1
):
    """helper to compute core thermal zone dict spec"""
    row_dict = {}
    row_dict["name"] = f"{bldg_area_type}_core_zone"
    row_dict["type"] = "core"
    row_dict["side"] = "core"
    row_dict["area"] = conditioned_floor_area - perimeter_area_sum
    row_dict["height"] = height
    row_dict["length"] = math.sqrt(row_dict["area"])
    row_dict["depth"] = row_dict["length"]
    row_dict["num_floors"] = num_floors
    return row_dict


def populate_std_schedules(case: Dict) -> Dict:
    """ populate hourly schedules based on standard input information

    Args:
        case: case dictionary. Properties used in this function are:
            - "weekly_occupied_hours"
            - "number_days_open_workday"
            - "number_days_open_weekend"

    Returns:
        hourly schedules dictionary

    """
    bldg_occ_sch_dict = sp.bldg_occ_sch(case)
    bldg_electric_equipment_sch_dict = sp.bldg_electric_equipment_sch(case)
    bldg_light_sch_dict = sp.bldg_light_sch(case)
    bldg_hvac_operation_sch_dict = sp.bldg_hvac_operation_sch(case)
    bldg_clg_setp_sch_dict = sp.bldg_clg_setp_sch(case)
    bldg_htg_setp_sch_dict = sp.bldg_htg_setp_sch(case)
    bldg_infiltration_sch_dict = sp.bldg_infiltration_sch(case)
    activity_sch_dict = sp.activity_sch()
    always_on_dict = sp.always_on()
    
    sch_list = [bldg_occ_sch_dict,
                bldg_electric_equipment_sch_dict,
                bldg_light_sch_dict,
                bldg_hvac_operation_sch_dict,
                bldg_clg_setp_sch_dict,
                bldg_htg_setp_sch_dict,
                bldg_infiltration_sch_dict,
                activity_sch_dict,
                always_on_dict]
    
    bldg_sch_dict = {}
    for ind,x in enumerate(["bldg_occ_sch",
                            "bldg_electric_equipment_sch",
                            "bldg_light_sch",
                            "bldg_hvac_operation_sch",
                            "bldg_clg_setp_sch",
                            "bldg_htg_setp_sch",
                            "bldg_infiltration_sch",
                            "activity_sch",
                            "always_on"]):
        bldg_sch_dict[str(ind)] = {}
        bldg_sch_dict[str(ind)]["name"] = x
        bldg_sch_dict[str(ind)]["type"] = "Any Number"
        bldg_sch_dict[str(ind)]["periods"] = {}
        bldg_sch_dict[str(ind)]["periods"]["0"] = {}
        bldg_sch_dict[str(ind)]["periods"]["0"]["through"] = "12/31"
        bldg_sch_dict[str(ind)]["periods"]["0"]["day_of_week"] = sch_list[ind]
    
    return bldg_sch_dict

def get_loads_fractions(fraction, load, bldg_a_t, loads_settings) -> Dict:
    """ lookup load fraction associated with building area type
    
    Args:
        fraction: list of fraction to retrieve
        load: load type
        bldg_a_t: building area type
        load_settings: dictionary containg the load fraction lookup values
    
    Returns:
        Dictionary of load fractions
    """
    fractions = {}
    for frac in fraction:
        # Lookup fraction associated with building area type
        if bldg_a_t in loads_settings[load][frac]:
            fractions[frac] = loads_settings[load][frac][bldg_a_t]
        # Lookup default fraction
        else:
            fractions[frac] = loads_settings[load][frac]["Any"]
    return fractions


def populate_std_loads(case: Dict) -> Dict:
    """ populate detailed internal load profiles for use in the processor

    Args:
        case: case dictionary. Properties used in this function are:
            - "people_density"
            - "lpd"
            - "plug_load_density"
            - "Infiltration_rate"

    Returns:
        ready to use loads dictionary for processor

    """
    loads_dict = {}
    loads_settings = read_json("loads_settings.json")
    if "plug_load_density" in case.keys():
        fractions = get_loads_fractions(
            ["frac_latent", "frac_radiant", "frac_lost"],
            "electric_equipment",
            case["building_area_type"],
            loads_settings,
        )
        loads_dict["electric_equipment"] = {
            "epd": case["plug_load_density"],
            "schedule": "bldg_electric_equipment_sch",
            "frac_latent": fractions["frac_latent"],
            "frac_radiant": fractions["frac_radiant"],
            "frac_lost": fractions["frac_lost"],
        }
    if "lpd" in case.keys():
        fractions = get_loads_fractions(
            ["frac_radiant", "frac_visible"],
            "lighting",
            case["building_area_type"],
            loads_settings,
        )
        loads_dict["lighting"] = {
            "lpd": case["lpd"],
            "schedule": "bldg_light_sch",
            "frac_radiant": fractions["frac_radiant"],
            "frac_visible": fractions["frac_visible"],
        }
    if "Infiltration_rate" in case.keys():
        loads_dict["infiltration"] = {
            "inf": case["Infiltration_rate"],
            "schedule": "bldg_infiltration_sch",
        }
    if "people_density" in case.keys():
        fractions = get_loads_fractions(
            ["frac_radiant"], "people", case["building_area_type"], loads_settings
        )
        loads_dict["people"] = {
            "people": case["people_density"],
            "schedule": "bldg_occ_sch",
            "activity_schedule": "activity_sch",
            "frac_radiant": fractions["frac_radiant"],
        }
    return loads_dict

def populate_std_constructions(case: Dict) -> Dict:
    """ populate detailed construction profiles for user in the processor
    Args:
        case: case dictionary. Properties used in this function are:
            - "wall_type"
            - "wall_u_factor"
            - "roof_type"
            - "roof_u_factor"
            - "window_U_factor"
            - "window_shgc"
    Returns:
        ready to use construction profile for processor
    """

    constructions = {
        "int_wall": {"type": "Default"},
        "int_floor": {"type": "Default"},
        "int_ceiling": {"type": "Default"},
        "ext_wall": {"type": case["wall_type"].strip().replace(' ', '_'), "u_factor": case["wall_u_factor"]},
        "roof": {"type": case["roof_type"].strip().replace(' ', '_'), "u_factor": case["roof_u_factor"]},
        "window": {"u_factor": case["window_U_factor"], "shgc": case["window_shgc"]},
    }

    return constructions


def populate_std_ground_temp_jan2dec(case: Dict) -> List:
    """

    Args:
        case: case dictionary. Properties used in this function are:
            - "epw_file": e.g. "USA_AZ_Tucson-Davis-Monthan.AFB.722745_TMY3.epw"

    Returns:
        List of ground temperature profile, from January to December, len=12

    """
    sample_return = [ # TODO: implement profile extraction logic. @Jeremy / @Jerry
        20.9,
        15.4,
        11.9,
        14.8,
        12.7,
        15.4,
        23.3,
        26.3,
        31.2,
        30.4,
        29.8,
        27.8,
    ]
    return sample_return
