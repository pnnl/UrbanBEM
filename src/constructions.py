from io import StringIO
from typing import Dict, List
import json
import pandas as pd
from geomeppy import IDF

from recipes import read_json, copy_idf_objects

IDF.setiddname("../resources/Energy+V9_0_1.idd")


class Constructions:
    INS_R_THRESH = 0.001

    def __init__(self, case: Dict, idf: IDF):
        self.case = case
        with open("../resources/construction_meta.json") as f:
            self.cons_meta = json.load(f)

        self.mat_dict = {}
        self.matnomass_dict = {}
        self.cons_list = []
        self.combinations = pd.DataFrame(
            columns=["applied_surface", "cons_name", "mat_name", "mat_type"]
        )

        self.identify_constructions()
        self.set_basic_constructions()
        self.set_ext_wall_constructions()
        self.set_roof_constructions()
        self.set_groundfloor_constructions()
        self.set_fenestration_constructions()

    def identify_constructions(self):
        pass

    def dfrow_from_meta(self, surface, type):
        """

        Args:
            surface: e.g. "ext_wall"
            type: e.g. "Wood_Framed"
            calculate_insulation: e.g. True

        Returns: None

        """

        row = {}
        original_mat_list = self.cons_meta["construction"][surface][type]
        row["applied_surface"] = surface
        row["cons_name"] = f"{surface.lower().strip()}_{type.lower().strip()}"

        # for mat in mat_list:
        #     if not self.mat_dict.has_key(mat):
        #         if self.cons_meta['material'].has_key(mat):
        #             self.mat_dict[mat] = self.cons_meta['material'][mat]
        #         if self.cons_meta['material_nomass'].has_key(mat):
        #             self.matnomass_dict[mat] = self.cons_meta['material_nomass'][mat]

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

        # TODO: currently, if there is no insulation layer, then we don't check for R value
        #  this might need to be changed
        if ins_mat_name is None:
            return mat_list

        # add air film resistance
        if "wall" in ins_mat_name:
            ext_air_r = 0.17
            int_air_r = 0.68
        elif "roof" in ins_mat_name:
            ext_air_r = 0.17
            int_air_r = 0.61
        else:
            print(
                "Cannot recognize insulation material name (no valid surface wihin), something is Wrong!"
            )
        nonins_sum_r = nonins_sum_r + ext_air_r + int_air_r

        # calculate insulation R
        if user_u_value > 1 / (nonins_sum_r + self.INS_R_THRESH):
            mat_list.pop(ins_mat_i)
        else:
            ins_r = (
                1 / user_u_value - nonins_sum_r
            )  # TODO: @Jeremy, double confirm the formula
            new_ins_mat_name = (
                f"{ins_mat_name}_R_{ins_r:.4f}"
            )  # build R rounding directly into material name f string
            mat_list[ins_mat_i] = new_ins_mat_name

        return mat_list

    def set_basic_constructions(self):
        pass

    def set_ext_wall_constructions(self):
        pass

    def set_roof_constructions(self):
        pass

    def set_groundfloor_constructions(self):
        pass

    def set_fenestration_constructions(self):
        pass
