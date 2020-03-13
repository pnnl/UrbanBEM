import math
from io import StringIO
import json
from typing import Dict
import pandas as pd
from geomeppy import IDF

IDF.setiddname("../resources/Energy+V9_0_1.idd")


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


def read_json(jsonpath: str) -> Dict:
    with open(jsonpath) as json_file:
        json_dict = json.load(json_file)
    return json_dict


def copy_idf_objects(to_idf, from_idf):
    """helper to copy all objects from `from_idf` to `to_idf`

    this is motivated by geomeppy being only able to set wwr for the whole idf, not for each zone separately. what was not working is shown below

            in `create_perimeter_zone' (run for each perimeter zone with a dfrow spec):
            self.idf.add_block(
                name=dfrow["name"],
                coordinates=coordinates,
                height=dfrow["height"],
                num_stories=1,
            )
            self.idf.set_default_constructions()
            self.idf.intersect_match()
            self.idf.set_wwr(wwr=dfrow["wwr"], orientation=dfrow["side"])

    """
    for objType in from_idf.idfobjects:
        if len(from_idf.idfobjects[objType]) > 0:
            for each in from_idf.idfobjects[objType]:
                to_idf.copyidfobject(each)
    return to_idf


class Geometry:

    # orient_list = ["south", "west", "north", "east"]
    # geo_spacing = 1.1
    # side2azimuth = {"south": 180, "west": 270, "north": 0, "east": 90}
    geometry_settings = read_json("geometry_settings.json")
    orient_list = geometry_settings["orient_list"]
    geo_spacing = geometry_settings["geo_spacing"]

    def __init__(self, init_thermalzone_df: pd.DataFrame):
        self.thermalzone_spec_df = self.set_geo_origins(init_thermalzone_df)
        self.idf = IDF("../resources/idfs/Minimal.idf")

        for i, dfrow in self.thermalzone_spec_df.iterrows():
            if dfrow["type"] == "perimeter":
                self.create_perimeter_zone(dfrow)
            if dfrow["type"] == "core":
                self.create_core_zone(dfrow)

    def set_geo_origins(self, df: pd.DataFrame) -> pd.DataFrame:
        original_index = df.index
        df.index = df["side"]
        df["origin_x"] = None
        df["origin_y"] = None

        # aux coordinates calculation
        x_center = (
            0.5
            * (
                max(
                    df.loc["south", "length"],
                    df.loc["core", "length"],
                    df.loc["north", "length"],
                )
                + df.loc["west", "depth"]
                + df.loc["east", "depth"]
            )
        ) * self.geo_spacing
        y_center = (
            0.5
            * (
                max(
                    df.loc["west", "length"],
                    df.loc["core", "length"],
                    df.loc["east", "length"],
                )
                + df.loc["south", "depth"]
                + df.loc["north", "depth"]
            )
        ) * self.geo_spacing

        df.loc["south", "origin_x"] = x_center - 0.5 * df.loc["south", "length"]
        df.loc["south", "origin_y"] = 0

        df.loc["north", "origin_x"] = x_center - 0.5 * df.loc["north", "length"]
        df.loc["north", "origin_y"] = 2 * y_center - df.loc["north", "depth"]

        df.loc["west", "origin_x"] = 0
        df.loc["west", "origin_y"] = y_center - 0.5 * df.loc["west", "length"]

        df.loc["east", "origin_x"] = 2 * x_center - df.loc["east", "depth"]
        df.loc["east", "origin_y"] = y_center - 0.5 * df.loc["east", "length"]

        df.loc["core", "origin_x"] = x_center - 0.5 * df.loc["core", "length"]
        df.loc["core", "origin_y"] = y_center - 0.5 * df.loc["core", "length"]

        return df

    def save_idf(self, path):
        self.idf.set_default_constructions()  # temparaty setting
        self.idf.saveas(path, lineendings="unix")

    @classmethod
    def from_total_areas(
        cls, bldg_area_type, conditioned_floor_area, gross_wall_area, wwr, height
    ):
        """constructor for gross area related inputs (i.e. CBECS like)

        Args:
            bldg_area_type: e.g. "office"
            conditioned_floor_area: e.g. 5502.6
            gross_wall_area: e.g. 3026
            wwr: window-to-wall ratio
            height: e.g. 15

        Returns:
            Geometry object with created thermal zones

        """
        floor2wall_ratio = conditioned_floor_area / gross_wall_area
        gross_wall_area_perimeter = 0.25 * gross_wall_area
        window_area_perimeter = gross_wall_area * wwr * 0.25

        init_thermalzone_df = pd.DataFrame()

        # add perimeter thermal zones spec
        for side in cls.orient_list:
            init_thermalzone_df = init_thermalzone_df.append(
                get_perimeter_row_dict(
                    bldg_area_type,
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
                    bldg_area_type, conditioned_floor_area, perimeter_area_sum, height
                ),
                ignore_index=True,
            )

        return cls(init_thermalzone_df)

    @classmethod
    def from_perimeter_areas(
        cls, bldg_area_type, conditioned_floor_area, height, perimeter_spec_dict: dict
    ):
        """

        Args:
            bldg_area_type: e.g. "office"
            conditioned_floor_area: e.g. 5502.6
            height: e.g. 15
            perimeter_spec_dict: needs to be specified in the following manner
                    spec_dict = {
                        "south": {"gross_wall_area": 909, "window_area": 222.2},
                        "west": {"gross_wall_area": 606, "window_area": 120.1},
                        "north": {"gross_wall_area": 909, "window_area": 180.1},
                        "east": {"gross_wall_area": 606, "window_area": 120.1},
                    }

        Returns:
            Geometry object with created thermal zones
        """
        # validate perimeter spec dict argument
        for k, v in perimeter_spec_dict.items():
            if k not in cls.orient_list:
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
        for side in cls.orient_list:
            spec_dict = perimeter_spec_dict[side]
            init_thermalzone_df = init_thermalzone_df.append(
                get_perimeter_row_dict(
                    bldg_area_type,
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
                    bldg_area_type, conditioned_floor_area, perimeter_area_sum, height
                ),
                ignore_index=True,
            )

        return cls(init_thermalzone_df)

    def create_perimeter_zone(self, dfrow):
        origin_x = dfrow["origin_x"]
        origin_y = dfrow["origin_y"]
        if dfrow["side"] in ["south", "north"]:
            delta_x = dfrow["length"]
            delta_y = dfrow["depth"]
        else:
            delta_x = dfrow["depth"]
            delta_y = dfrow["length"]

        coordinates = [
            (origin_x + delta_x, origin_y),
            (origin_x + delta_x, origin_y + delta_y),
            (origin_x, origin_y + delta_y),
            (origin_x, origin_y),
        ]

        local_idf = IDF(StringIO(""))
        local_idf.add_block(
            name=dfrow["name"],
            coordinates=coordinates,
            height=dfrow["height"],
            num_stories=1,
        )
        local_idf.intersect_match()
        local_idf.set_wwr(wwr=dfrow["wwr"], orientation=dfrow["side"])

        self.idf = copy_idf_objects(self.idf, local_idf)

    def create_core_zone(self, dfrow):
        origin_x = dfrow["origin_x"]
        origin_y = dfrow["origin_y"]
        coordinates = [
            (origin_x + dfrow["length"], origin_y),
            (origin_x + dfrow["length"], origin_y + dfrow["depth"]),
            (origin_x, origin_y + dfrow["depth"]),
            (origin_x, origin_y),
        ]

        local_idf = IDF(StringIO(""))
        local_idf.add_block(
            name=dfrow["name"],
            coordinates=coordinates,
            height=dfrow["height"],
            num_stories=1,
        )
        local_idf.intersect_match()
        self.idf = copy_idf_objects(self.idf, local_idf)


def main():

    pd.set_option("max_columns", 10)
    print("Test case for gross area etc constructor")
    geoObj1 = Geometry.from_total_areas(
        "office", 5502.6374, 3026, 0.212042628774423, 15
    )
    print(geoObj1.thermalzone_spec_df)

    geoObj1.save_idf("../devoutput/genObj1.idf")

    spec_dict = {
        "south": {"gross_wall_area": 909, "window_area": 222.2},
        "west": {"gross_wall_area": 606, "window_area": 120.1},
        "north": {"gross_wall_area": 909, "window_area": 180.1},
        "east": {"gross_wall_area": 606, "window_area": 120.1},
    }

    print("\nTest case for perimeter spec etc constructor")
    geoObj2 = Geometry.from_perimeter_areas("office", 5502.6, 15, spec_dict)
    print(geoObj2.thermalzone_spec_df)

    geoObj2.save_idf("../devoutput/genObj2.idf")

    print(
        "\nOpen ../devoutput/genObjx.idf in Sketchup to check geometry objects results visually."
    )


if __name__ == "__main__":
    main()
