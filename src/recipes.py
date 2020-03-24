import json
import math
import numbers
from typing import Dict


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


def convert_dict_unit(imp: Dict) -> Dict:
    si = {}

    unit_conv_dict = {  # borrowed from modelkit
        "in": 0.0254,
        "ft": 0.3048,
        "ft2": 0.3048 * 0.3048,
        "ft3": 0.3048 * 0.3048 * 0.3048,
        "delta_f": 5.0 / 9.0,
        "cfm": 1.0 / 2118.88,
        "gal": 1.0 / 264.1721,
        "gpm": 1.0 / 15850.32,
        "ft_h2o": 2989.0,
        "in_h2o": 249.089,
        "btuh": 1.0 / 3.415179,
        "hp": 745.6999,
        "r_value": 0.1761,
        "conductivity": 1.731,
        "density": 16.02,
        "cp": 4187,
    }
    unit_name_map = {  # currently useless
        "in": "m",
        "ft": "m",
        "ft2": "m2",
        "ft3": "m3",
        "delta_f": "delta_c",
        "cfm": "",
        "gal": "",
        "gpm": "",
        "ft_h2o": "",
        "in_h2o": "",
        "btuh": "",
        "hp": "",
        "r_value": "",
        "conductivity": "",
        "density": "",
        "cp": "",
    }

    for key, value in imp.items():
        si_key = key
        si_val = value  # by default, no change
        if isinstance(value, dict):  # recursively check sub levels
            si_val = convert_dict_unit(value)
        if isinstance(value, numbers.Number):
            for unit_key, unit_factor in unit_conv_dict.items():
                if f"({unit_key})" in key:
                    si_val = value * unit_factor
                    # si_key = key.replace(unit_key, unit_name_map[unit_key])
                    si_key = key.replace(f"({unit_key})", "").strip()
                    break
        si[si_key] = si_val
    return si