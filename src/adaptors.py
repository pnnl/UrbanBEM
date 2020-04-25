""" Data transformers and wrappers"""
import math
from typing import Dict
from recipes import read_json
import pandas as pd

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
    # TODO: @Yunyang, please replace the contents of this function with the schedule derivation logic
    #  schedules_sample contains exact structure we need as the output of the schedule logic you are coding.
    import json

    with open("processed_schedule_sample.json") as f:
        schedules_sample = json.load(f)
    return schedules_sample


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
