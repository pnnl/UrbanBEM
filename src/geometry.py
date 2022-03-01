from io import StringIO
from typing import Dict

import pandas as pd
from geomeppy import IDF

from recipes import read_json, copy_idf_objects

IDF.setiddname("../resources/V9-5-0-Energy+.idd")


class Geometry:

    geometry_settings = read_json("geometry_settings.json")
    orient_list = geometry_settings["orient_list"]
    geo_spacing = geometry_settings["geo_spacing"]

    def __init__(self, case: Dict, idf: IDF):
        self.case = case
        init_thermalzone_df = pd.DataFrame.from_dict(
            case["zone_geometry"], orient="index"
        )
        self.thermalzone_spec_df = self.set_geo_origins(init_thermalzone_df)
        self.idf = idf

        for i, dfrow in self.thermalzone_spec_df.iterrows():
            if dfrow["type"] == "perimeter":
                self.create_perimeter_zone(dfrow)
            if dfrow["type"] == "core":
                self.create_core_zone(dfrow)
        self.set_int_wall_conditions()
        self.create_zone_list()

    def set_int_wall_conditions(self):
        windows = self.idf.idfobjects["FENESTRATIONSURFACE:DETAILED"]
        window_walls = [
            win["Building_Surface_Name"].strip().lower()
            for win in windows
            if str(win["Surface_Type"]).strip().lower() == "window"
        ]
        unique_window_walls = list(set(window_walls))

        surfaces = self.idf.idfobjects["BUILDINGSURFACE:DETAILED"]
        int_walls = []
        for surface in surfaces:
            if (
                str(surface["Surface_Type"]).strip().lower() != "wall"
            ):  # skip if it is not a wall
                continue
            if (
                str(surface["Name"]).strip().lower() in unique_window_walls
            ):  # skip if it is a window wall
                continue

            # set int_wall conditions
            surface["Outside_Boundary_Condition"] = "Adiabatic"
            surface["Sun_Exposure"] = "NoSun"
            surface["Wind_Exposure"] = "NoWind"
            surface["View_Factor_to_Ground"] = 0

    def set_geo_origins(self, df: pd.DataFrame) -> pd.DataFrame:
        df.index = df["side"]

        has_core = "core" in df.index

        if has_core:
            core_length = df.loc["core", "length"]
        else:
            core_length = 0

        df["origin_x"] = None
        df["origin_y"] = None

        # aux coordinates calculation
        x_center = (
            0.5
            * (
                max(df.loc["south", "length"], core_length, df.loc["north", "length"])
                + df.loc["west", "depth"]
                + df.loc["east", "depth"]
            )
        ) * self.geo_spacing
        y_center = (
            0.5
            * (
                max(df.loc["west", "length"], core_length, df.loc["east", "length"])
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

        if has_core:
            df.loc["core", "origin_x"] = x_center - 0.5 * core_length
            df.loc["core", "origin_y"] = y_center - 0.5 * core_length

        return df

    def save_idf(self, path):
        self.idf.saveas(path, lineendings="unix")

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
            height=dfrow["height"] * int(dfrow["num_floors"]),
            num_stories=int(dfrow["num_floors"]),
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
            height=dfrow["height"] * int(dfrow["num_floors"]),
            num_stories=int(dfrow["num_floors"]),
        )
        local_idf.intersect_match()
        self.idf = copy_idf_objects(self.idf, local_idf)

    def create_zone_list(self):
        local_idf = IDF(StringIO(""))
        zonelist_kwargs = {
            "key": "ZONELIST",
            "Name": f"zone_list_{self.case['building_area_type'].strip()}",
        }
        field_num = 0
        for zn in self.idf.idfobjects["ZONE"]:
            field_num += 1
            zonelist_kwargs[f"Zone_{int(field_num)}_Name"] = zn.Name
        local_idf.newidfobject(**zonelist_kwargs)
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
