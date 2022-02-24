from io import StringIO
from typing import Dict, List
import json
import pandas as pd
from geomeppy import IDF

from recipes import read_json, copy_idf_objects

IDF.setiddname("../resources/Energy+V9_5_0.idd")


class Constructions:
    INS_R_THRESH = 0.001

    def __init__(self, case: Dict, idf: IDF):
        self.idf = idf
        self.case = case
        with open("../resources/construction_meta.json") as f:
            self.cons_meta = json.load(f)

        self.mat_dict = {}
        self.cons_dict = {}

        self.constructions = self.case["constructions"]
        for surface, contents in self.constructions.items():
            if surface in ["int_wall", "int_floor", "int_ceiling", "ext_wall", "roof"]:
                if "u_factor" in contents:
                    self.set_a_typical_construction(
                        surface, contents["type"], contents["u_factor"]
                    )
                else:
                    self.set_a_typical_construction(surface, contents["type"])

        self.add_typical_materials()
        self.add_typical_constructions()

        self.set_window_allin1(
            self.constructions["window"]["u_factor"],
            self.constructions["window"]["shgc"],
        )

        self.set_ground_floors()
        self.add_ground_temp_profile()

    def save_idf(self, path):
        self.idf.saveas(path, lineendings="unix")

    def set_ground_floors(self):
        """The perimeter surface would use the F-factor method and the core zone be modeled as having a outside boundary
            condition being adiabatic.
        On top of the of the Construction objects we need to add a Site:GroundTemperature:FCfactorMethod object.
        The temperature inputs in the object have to be the average monthly outdoor air temperature delayed by 3 months.
        This can easily be done by parsing the .stat file corresponding the .epw file used for the simulation.
        """

        # for each zone in case, find corresponding ground floors and add Ffactor contruction
        for zone_id, zone in self.case["zone_geometry"].items():
            if zone["type"] == "core":
                ground_cons_name = f"{zone['name']}_core_bottom_floor_ffactor"
                perimeter_exposed = 0
                outside_boundary_condition = "Adiabatic"
            else:
                ground_cons_name = f"{zone['name']}_perimeter_bottom_floor_ffactor"
                perimeter_exposed = zone["length"]
                outside_boundary_condition = "GroundFCfactorMethod"

            # add construction
            self.idf.newidfobject(
                "Construction:FfactorGroundFloor".upper(),
                Name=ground_cons_name,
                FFactor=self.cons_meta["construction_ffactorgroundfloor"]["FFactor"],
                Area=zone["area"],
                PerimeterExposed=perimeter_exposed,
            )

            # find matching surfacen and modify reference
            surfaces = self.idf.idfobjects["BuildingSurface:Detailed".upper()]
            foundSurface = False
            for surface in surfaces:
                if (
                    ("Storey 0".lower() in surface["Name"].lower())
                    and (zone["name"].lower() in surface["Name"].lower())
                    and (surface["Surface_Type"].lower().strip() == "floor")
                ):
                    surface["Construction_Name"] = ground_cons_name
                    surface["Outside_Boundary_Condition"] = outside_boundary_condition
                    foundSurface = True

            if not foundSurface:
                print(f"No ground floor found for {zone['name']}. Something is wrong!")

    def add_ground_temp_profile(self):
        ground_temp_list = self.constructions["ground_temp_profile_jan2dec"]
        # sanity check
        if len(ground_temp_list) != 12:
            print(
                f"Ground temperature length is {len(ground_temp_list)} instead of 12. Wrong!"
            )
            return
        site_obj = self.idf.newidfobject("SITE:GROUNDTEMPERATURE:FCFACTORMETHOD")
        i = 0
        for field in site_obj["objls"][1:]:  # iterature over jan to dec
            site_obj[field] = ground_temp_list[i]
            i += 1

    def set_window_allin1(self, u_factor, shgc):

        winmat_name = f"glazing_u_{u_factor:.4f}_shgc_{shgc:.4f}"
        wincons_name = f"window_u_{u_factor:.4f}_shgc_{shgc:.4f}"

        # add window material
        self.idf.newidfobject(
            "WindowMaterial:SimpleGlazingSystem".upper(),
            Name=winmat_name,
            UFactor=u_factor,
            Solar_Heat_Gain_Coefficient=shgc,
        )

        # add window construction
        self.idf.newidfobject(
            "Construction".upper(), Name=wincons_name, Outside_Layer=winmat_name
        )

        # refer to window construction
        windows = self.idf.idfobjects["FENESTRATIONSURFACE:DETAILED"]
        self.batch_modify_idf_objs(windows, dict(Construction_Name=wincons_name))

    def set_a_typical_construction(self, surface, type, u_factor=None):
        """set construction for one of the following
            "int_wall", "int_floor", "int_ceiling", "ext_wall", "roof"
        """

        # inject construction and materials to dict
        construction_name = f"{surface.lower().strip()}_{type.lower().strip()}"
        original_mat_list = self.cons_meta["construction"][surface][type]
        if u_factor is None:
            adj_mat_list = original_mat_list
        else:
            adj_mat_list = self.get_adj_r_matlist(original_mat_list, u_factor)

        # add construction to const dict
        if not (construction_name in self.cons_dict):
            self.cons_dict[construction_name] = adj_mat_list

        # add corresponding materials to mat dict
        for mat in adj_mat_list:
            if mat in self.mat_dict:
                continue
            else:
                if "_ins_layer_R" in mat:
                    r_float = float(
                        mat.split("_R_")[-1]
                    )  # read r float from the adj mat name
                    mat_prefix = str(
                        mat.split("_R_")[0]
                    )  # read original mat name from the adj mat name

                    self.mat_dict[mat] = self.cons_meta["material"][
                        mat_prefix
                    ]  # add original properties first
                    self.mat_dict[mat][
                        "Thermal_Resistance"
                    ] = r_float  # then modify R value
                else:
                    self.mat_dict[mat] = self.cons_meta["material"][mat]

        # add construction reference to surface objects (cons / mat idf objs will be added later altogether)
        # need to deal with different surfface separately
        if surface == "int_wall":
            walls = self.idfobjs_filters(
                "BUILDINGSURFACE:DETAILED", dict(Surface_Type="wall")
            )
            self.batch_modify_idf_objs(walls, dict(Construction_Name=construction_name))
        if surface == "int_floor":
            floors = self.idfobjs_filters(
                "BUILDINGSURFACE:DETAILED", dict(Surface_Type="floor")
            )
            self.batch_modify_idf_objs(
                floors, dict(Construction_Name=construction_name)
            )
        if surface == "int_ceiling":
            ceilings = self.idfobjs_filters(
                "BUILDINGSURFACE:DETAILED", dict(Surface_Type="ceiling")
            )
            self.batch_modify_idf_objs(
                ceilings, dict(Construction_Name=construction_name)
            )
        if surface == "ext_wall":
            windows = self.idfobjs_filters(
                "FENESTRATIONSURFACE:DETAILED", dict(Surface_Type="window")
            )
            ext_wall_combined_list = [obj["Building_Surface_Name"] for obj in windows]
            ext_wall_unique_list = list(set(ext_wall_combined_list))
            ext_walls = []
            walls = self.idfobjs_filters(
                "BUILDINGSURFACE:DETAILED", dict(Surface_Type="wall")
            )
            for wall in walls:
                if wall["Name"] in ext_wall_unique_list:
                    ext_walls.append(wall)
            self.batch_modify_idf_objs(
                ext_walls, dict(Construction_Name=construction_name)
            )
        if surface == "roof":
            roofs = self.idfobjs_filters(
                "BUILDINGSURFACE:DETAILED", dict(Surface_Type="roof")
            )
            self.batch_modify_idf_objs(roofs, dict(Construction_Name=construction_name))

    def add_typical_materials(self):
        for mat_name, mat_props in self.mat_dict.items():
            obj_type = mat_props.pop("obj_type").lower().strip()
            if obj_type == "default":
                mat_props["key"] = "MATERIAL"
            elif obj_type == "nomass":
                mat_props["key"] = "MATERIAL:NOMASS"
            else:
                print("material obj type is not valid!")

            mat_props["Name"] = mat_name
            self.idf.newidfobject(**mat_props)

    def add_typical_constructions(self):
        for const_name, mat_list in self.cons_dict.items():
            const_props = {"key": "CONSTRUCTION", "Name": const_name}
            layer_id = 1
            for mat in mat_list:
                if layer_id == 1:
                    const_props["Outside_Layer"] = mat
                else:
                    const_props[f"Layer_{int(layer_id)}"] = mat
                layer_id += 1
            self.idf.newidfobject(**const_props)

    def idfobjs_filters(self, obj_type, property_dict: Dict):
        original_objs = self.idf.idfobjects[obj_type.upper()]
        filtered_objs = []
        for property, value in property_dict.items():
            for obj in original_objs:
                if obj[property].lower() == value.lower():
                    filtered_objs.append(obj)
            original_objs = filtered_objs
        return filtered_objs

    def batch_modify_idf_objs(self, objs, property_dict: Dict):
        for property, value in property_dict.items():
            for obj in objs:
                obj[property] = value

    def get_adj_r_matlist(self, mat_list: List, user_u_value: float) -> List:
        """mat_list adjusted with computed r value

        Args:
            mat_list: material name list of a construction
            user_u_value: desired construction u value read from standard input

        Returns:
                - if an insulation layer is presented and needed based on u value, then modify insulation layer name to
                    reflect its r value
                - if an insulation layer is not presented, then return original material list
                - if an insulation layer is presented but not needed, then return original material list without
                    insulation layer

        """

        # find insulation material and get non-insulation r sum
        ins_mat_name = None
        ins_mat_i = None
        nonins_sum_r = 0
        i = 0
        for mat in mat_list:
            if "ins_layer" in mat.lower().strip():
                if ins_mat_name is not None:
                    print(
                        "More than 1 insulaion layer in one construction, something is Wrong!"
                    )
                ins_mat_name = mat.lower().strip()
                ins_mat_i = i
            else:
                mat_properties = self.cons_meta["material"][mat]
                if mat_properties["obj_type"].lower().strip() == "default":
                    nonins_sum_r += (
                        mat_properties["Thickness"] / mat_properties["Conductivity"]
                    )
                elif mat_properties["obj_type"].lower().strip() == "nomass":
                    nonins_sum_r += mat_properties["Thermal_Resistance"]
                else:
                    print(
                        "Cannot get R value from non-insulation material, something is Wrong!"
                    )
            i += 1

        # TODO: currently, if there is no insulation layer, then we don't check for R value
        #  this might need to be changed
        if ins_mat_name is None:
            return mat_list

        # add air film resistance
        if "wall" in ins_mat_name:
            ext_air_r = 0.17 * 0.17611
            int_air_r = 0.68 * 0.17611
        elif "roof" in ins_mat_name:
            ext_air_r = 0.17 * 0.17611
            int_air_r = 0.61 * 0.17611
        else:
            print(
                "Cannot recognize insulation material name (no valid surface wihin), something is Wrong!"
            )
        nonins_sum_r = nonins_sum_r + ext_air_r + int_air_r

        # calculate insulation R
        if user_u_value > 1 / (nonins_sum_r + self.INS_R_THRESH):
            mat_list.pop(ins_mat_i)
        else:
            ins_r = 1 / user_u_value - nonins_sum_r
            new_ins_mat_name = (
                f"{ins_mat_name}_R_{ins_r:.4f}"
            )  # build R rounding directly into material name f string
            mat_list[ins_mat_i] = new_ins_mat_name

        return mat_list


def main():
    import os

    os.chdir("/mnt/c/FirstClass/airflow/dags/urban-sim-flow/src")  # for linux
    idf = IDF("../devoutput/geometry_added.idf")
    casename = "cbecs5"
    with open(f"../input/processed_inputs/{casename}_processed.json") as f:
        proc_case = json.load(f)

    # manually change proc_case ext wall and roof u value to trigger / test branch of adjusting insulation layer r value
    proc_case["constructions"]["ext_wall"]["u_factor"] = 3
    proc_case["constructions"]["roof"]["u_factor"] = 4

    const_obj = Constructions(proc_case, idf)
    const_obj.save_idf("../devoutput/const_test.idf")


if __name__ == "__main__":
    main()
