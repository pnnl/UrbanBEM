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
    """populate hourly schedules based on standard input information

    Args:
        case: case dictionary. Properties used in this function are:
            - "weekly_occupied_hours"
            - "number_days_open_workday"
            - "number_days_open_weekend"

    Returns:
        hourly schedules dictionary

    """
    bldg_business_hour, consider_lunch_time = sp.bldg_business_hour(
        case, randomizeHours=False
    )
    bldg_occ_sch_dict = sp.bldg_occ_sch(bldg_business_hour, consider_lunch_time)
    bldg_swh_use_sch_dict = sp.schdule_dict_multiplier(
        sp.bldg_occ_sch(bldg_business_hour, False), multiplier=0.1
    )  # swh use schedule is 0.1 x occ without lunch break
    bldg_electric_equipment_sch_dict = sp.bldg_electric_equipment_sch(bldg_occ_sch_dict)
    bldg_gas_equipment_sch_dict = (
        bldg_electric_equipment_sch_dict  # TODO: this needs to be replaced.
    )
    bldg_light_sch_dict = sp.bldg_light_sch(bldg_business_hour, consider_lunch_time)
    bldg_ext_light_sch_dict = bldg_light_sch_dict  # TODO: this needs to be replaced.
    bldg_hvac_operation_sch_dict = sp.bldg_hvac_operation_sch(
        bldg_business_hour, consider_lunch_time
    )
    bldg_clg_setp_sch_dict = sp.bldg_clg_setp_sch(bldg_hvac_operation_sch_dict)
    bldg_htg_setp_sch_dict = sp.bldg_htg_setp_sch(bldg_hvac_operation_sch_dict)
    bldg_infiltration_sch_dict = sp.bldg_infiltration_sch(bldg_hvac_operation_sch_dict)
    bldg_door_infiltration_sch_dict = (
        bldg_infiltration_sch_dict  # TODO: this needs to be replaced.
    )
    activity_sch_dict = sp.activity_sch()
    always_on_dict = sp.always_on()

    sch_dict = {
        "bldg_occ_sch": bldg_occ_sch_dict,
        "bldg_swh_use_sch": bldg_swh_use_sch_dict,
        "bldg_electric_equipment_sch": bldg_electric_equipment_sch_dict,
        "bldg_gas_equipment_sch": bldg_gas_equipment_sch_dict,
        "bldg_light_sch": bldg_light_sch_dict,
        "bldg_ext_light_sch": bldg_ext_light_sch_dict,
        "bldg_hvac_operation_sch": bldg_hvac_operation_sch_dict,
        "bldg_clg_setp_sch": bldg_clg_setp_sch_dict,
        "bldg_htg_setp_sch": bldg_htg_setp_sch_dict,
        "bldg_infiltration_sch": bldg_infiltration_sch_dict,
        "bldg_door_infiltration_sch": bldg_door_infiltration_sch_dict,
        "activity_sch": activity_sch_dict,
        "always_on": always_on_dict,
    }

    bldg_sch_dict = {}
    ind = 0
    for k, v in sch_dict.items():
        bldg_sch_dict[str(ind)] = {}
        bldg_sch_dict[str(ind)]["name"] = k
        bldg_sch_dict[str(ind)]["type"] = "Any Number"
        bldg_sch_dict[str(ind)]["periods"] = {}
        bldg_sch_dict[str(ind)]["periods"]["0"] = {}
        bldg_sch_dict[str(ind)]["periods"]["0"]["through"] = "12/31"
        bldg_sch_dict[str(ind)]["periods"]["0"]["day_of_week"] = v
        ind += 1

    return bldg_sch_dict


def get_loads_fractions(fraction, load, bldg_a_t, loads_settings) -> Dict:
    """lookup load fraction associated with building area type

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
    """populate detailed internal load profiles for use in the processor

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
    if "gas_equipment_load" in case.keys():
        fractions = get_loads_fractions(
            ["frac_latent", "frac_radiant", "frac_lost"],
            "gas_equipment",
            case["building_area_type"],
            loads_settings,
        )
        loads_dict["gas_equipment"] = {
            "watts": case["gas_equipment_load"],
            "schedule": "bldg_gas_equipment_sch",
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

    if "ext_light_level" in case.keys():
        loads_dict["ext_lighting"] = {
            "design_level": case["ext_light_level"],
            "schedule": "bldg_ext_light_sch",
        }

    if "infiltration_rate" in case.keys():
        loads_dict["infiltration"] = {
            "inf": case["infiltration_rate"],
            "schedule": "bldg_infiltration_sch",
        }
    if "door_infiltration_rate" in case.keys():
        loads_dict["door_infiltration"] = {
            "inf": case["door_infiltration_rate"],
            "schedule": "bldg_door_infiltration_sch",
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
    """populate detailed construction profiles for user in the processor
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
        "ext_wall": {
            "type": case["wall_type"].strip().replace(" ", "_").replace("-", "_"),
            "u_factor": case["wall_u_factor"],
        },
        "roof": {
            "type": case["roof_type"].strip().replace(" ", "_").replace("-", "_"),
            "u_factor": case["roof_u_factor"],
        },
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
    sample_return = [
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

    weather_key = case["epw_file"].split(".epw")[0].strip()
    temperatures_json = read_json("../resources/monthlydrybulbtemp_dailyavg.json")
    if weather_key in temperatures_json:
        drybulb_temps = temperatures_json[weather_key]
    else:
        print("Does not find dry bulb temperature key, will use default. Please Fix!")
        return sample_return

    ground_temps = drybulb_temps[-3:] + drybulb_temps[:9]

    return ground_temps


def populate_std_hvac_for_osstd(case: Dict) -> Dict:
    """populate detailed dictionary for openstudio standard function call (bare minimum is the *s below)
        def model_add_hvac_system(model,
        *                    system_type,
        *                    main_heat_fuel,
        *                    zone_heat_fuel,
        *                    cool_fuel,
                            zones,
                            hot_water_loop_type: 'HighTemperature',
                            chilled_water_loop_cooling_type: 'WaterCooled',
                            heat_pump_loop_cooling_type: 'EvaporativeFluidCooler',
                            air_loop_heating_type: 'Water',
                            air_loop_cooling_type: 'Water',
                            zone_equipment_ventilation: true,
                            fan_coil_capacity_control_method: 'CyclingFan')

    Args:
        case: case dictionary. Properties used in this function are:
            - "hvac_system_type": e.g. "PSZ, Gas, SingleSpeedDX"

    Returns:

    """

    hvac = {
        "hvac_type": case["hvac_system_type"]
        .strip()
        .replace(",", "_")
        .replace(" ", ""),
    }

    return hvac


def populate_std_swh_for_osstd(case: Dict) -> Dict:
    """populate service water heating related info

    Args:
        case: case dictionary. Properties used in this function are:
            - "hvac_system_type": e.g. "PSZ, Gas, SingleSpeedDX"

    Returns:

    """

    swh = {
        "main_water_heater_fuel": case["service_water_heater_fuel"].strip(),
        "main_service_water_peak_flowrate": case["service_water_peak_flowrate"],
    }

    return swh
