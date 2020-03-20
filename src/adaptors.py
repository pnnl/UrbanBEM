""" Data transformers and wrappers"""
import math
from typing import Dict
from recipes import read_json
import pandas as pd

geometry_settings = read_json("geometry_settings.json")
orient_list = geometry_settings["orient_list"]


def populate_cbecs_zones(case: Dict) -> Dict:
    building_area_type = case["building_area_type"]
    conditioned_floor_area = case["geometry_spec"]["conditioned_floor_area"]
    gross_wall_area = case["geometry_spec"]["gross_wall_area"]
    wwr = case["geometry_spec"]["wwr"]
    height = case["geometry_spec"]["height"]

    floor2wall_ratio = conditioned_floor_area / gross_wall_area
    gross_wall_area_perimeter = 0.25 * gross_wall_area
    window_area_perimeter = gross_wall_area * wwr * 0.25

    init_thermalzone_df = pd.DataFrame()

    # add perimeter thermal zones spec
    for side in orient_list:
        init_thermalzone_df = init_thermalzone_df.append(
            get_perimeter_row_dict(
                building_area_type,
                side,
                gross_wall_area_perimeter,
                floor2wall_ratio,
                height,
                window_area_perimeter,
            ),
            ignore_index=True,
        )

    # add core zone spec if needed
    if floor2wall_ratio > 1.25:
        perimeter_area_sum = init_thermalzone_df["area"].sum()
        init_thermalzone_df = init_thermalzone_df.append(
            get_core_row_dict(
                building_area_type, conditioned_floor_area, perimeter_area_sum, height
            ),
            ignore_index=True,
        )

    init_thermalzone_dict = init_thermalzone_df.to_dict(orient="index")
    return init_thermalzone_dict


def populate_comcheck_zones(case: Dict) -> Dict:
    building_area_type = case["building_area_type"]
    conditioned_floor_area = case["geometry_spec"]["conditioned_floor_area"]
    height = case["geometry_spec"]["height"]
    perimeter_spec_dict = case["geometry_spec"]["perimeter_spec_dict"]

    # validate perimeter spec dict argument
    for k, v in perimeter_spec_dict.items():
        if k not in orient_list:
            print(
                'ERROR: perimeter spec dict key values need to be among ["south", "west", "north", "east"]'
            )
            return None
        if isinstance(v, dict):
            for vk, vv in v.items():
                if vk not in ["gross_wall_area", "window_area"]:
                    print(
                        'ERROR: perimeter spec for each orientation dict needs keys ["gross_wall_area", "window_area"]'
                    )
        else:
            print("ERROR: perimeter spec for each orientation needs to be a dict")

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
            ),
            ignore_index=True,
        )

    # add core zone spec if needed
    if floor2wall_ratio > 1.25:
        perimeter_area_sum = init_thermalzone_df["area"].sum()
        init_thermalzone_df = init_thermalzone_df.append(
            get_core_row_dict(
                building_area_type, conditioned_floor_area, perimeter_area_sum, height
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
    return row_dict


def get_core_row_dict(
    bldg_area_type, conditioned_floor_area, perimeter_area_sum, height
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
    return row_dict
