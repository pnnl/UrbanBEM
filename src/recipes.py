import json, os
import numbers
from typing import Dict, List
from types import LambdaType
from eppy.modeleditor import IDF

print(os.getcwd())


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
                # check if to_idf already has object with same name
                # (occationally it has no name but a zone list name for instance, so I use index [1] instead of .Name)
                # and object type, if so, skip
                existing_names = [
                    idfobj.obj[1].strip().lower()
                    for idfobj in to_idf.idfobjects[each.key.upper()]
                ]
                if each.obj[1].strip().lower() in existing_names:
                    continue
                to_idf.copyidfobject(each)
    return to_idf


def convert_dict_unit(imp: Dict) -> (Dict, Dict):
    si = {}
    si_clean = {}

    # conversion is either defined as a simple scaling factor or a lambda (e.g. F to C conversion)
    unit_conv_dict = {  # modified from modelkit, units not used are commented out.
        "in": 0.0254,
        "ft": 0.3048,
        "ft2": 0.3048 * 0.3048,
        "ft3": 0.3048 * 0.3048 * 0.3048,
        "Btu/h-ft2-F": 5.678263,
        "people/1000ft2": 1 / 1000 / (0.3048 * 0.3048),
        "W/ft2": 1 / (0.3048 * 0.3048),
        "cfm/ft2": 5.08e-3,
        "hr/wk": 1,
        "cfm/person": 1.0 / 2118.88,
        "gal/min": 6.309e-5,
        "F": (lambda x: (x - 32) * 5 / 9)
        # "delta_f": 5.0 / 9.0,
        # "cfm": 1.0 / 2118.88,
        # "gal": 1.0 / 264.1721,
        # "gpm": 1.0 / 15850.32,
        # "ft_h2o": 2989.0,
        # "in_h2o": 249.089,
        # "btuh": 1.0 / 3.415179,
        # "hp": 745.6999,
        # "r_value": 0.1761,
        # "conductivity": 1.731,
        # "density": 16.02,
        # "cp": 4187,
    }
    unit_name_map = {
        "in": "m",
        "ft": "m",
        "ft2": "m2",
        "ft3": "m3",
        "Btu/h-ft2-F": "W/m2-K",
        "people/1000ft2": "person/m2",
        "W/ft2": "W/m2",
        "cfm/ft2": "m3/s-m2",
        "hr/wk": "hr/wk",
        "cfm/person": "m3/s-person",
        "gal/min": "m3/s",
        "F": "C",
        # "delta_f": "delta_c",
        # "cfm": "m3/s",
        # "gal": "",
        # "gpm": "",
        # "ft_h2o": "",
        # "in_h2o": "",
        # "btuh": "",
        # "hp": "",
        # "r_value": "",
        # "conductivity": "",
        # "density": "",
        # "cp": "",
    }

    for key, value in imp.items():
        si_key = key
        si_clean_key = key
        si_val = value  # by default, no change
        if isinstance(value, dict):  # recursively check sub levels
            si_val = convert_dict_unit(value)
        if isinstance(value, numbers.Number):
            for unit_key, unit_factor in unit_conv_dict.items():
                if f"({unit_key})" in key:
                    if isinstance(unit_factor, LambdaType):
                        si_val = unit_factor(value)
                    else:
                        si_val = value * unit_factor
                    # si_key = key.replace(unit_key, unit_name_map[unit_key])
                    si_key = key.replace(
                        f"({unit_key})", f"({unit_name_map[unit_key]})"
                    ).strip()
                    si_clean_key = key.replace(f"({unit_key})", "").strip()
                    break
        si_clean_key = si_clean_key.split("(")[0].strip()
        si[si_key] = si_val
        si_clean[si_clean_key] = si_val
    return si, si_clean


def batch_modify_idf_objs(objs, property_dict: Dict):
    for property, value in property_dict.items():
        for obj in objs:
            obj[property] = value


def get_containing_object_types(idf: IDF, print_out=False) -> List:
    results = []
    totalnum = 0
    for key, val in idf.idfobjects.items():
        if len(val) > 0:
            results.append(key)
            if print_out:
                print(f"{key}: {len(val)}")
            totalnum += len(val)
    if print_out:
        print(f"Total number of objects: {totalnum}")
        print("\n **** \n")
    return results


def get_object_by_types(idf: IDF, types: List, ignore_error=True) -> List:
    types = [type.upper().strip() for type in types]
    all_objs = []
    for type in types:
        objs = idf.idfobjects[type.upper().strip()]
        if len(objs) == 0 and (not ignore_error):
            print(f"ERROR: {type} does not exist in the idf")
            continue
        all_objs.extend(list(objs))
    return all_objs


def get_object_not_in_types(idf: IDF, types: List) -> List:
    types = [type.upper().strip() for type in types]
    exc_objs = []
    all_types = get_containing_object_types(idf)
    for type in all_types:
        if type not in types:
            objs = idf.idfobjects[type.upper().strip()]
            if len(objs) == 0:
                print("Somthing is wrong!")
                continue
            exc_objs.extend(list(objs))
    return exc_objs


def to_cbsa_hvac_type(case):
    """
    Inputs:
    -case: case json file for a building (either before or after cleaning)

    Outputs:
    -case_hvac_converted: case json file for a building with updated HVAC type name, if CBSA or RBSA, then it's converted to CBECS HVAC naming, otherwise no change
    """
    # Open the mapping JSON file
    f_hvac_type = open("hvac_type_name_mapping.json", encoding="utf-8")

    # Returns JSON object as a dictionary
    data_hvac_type = json.load(f_hvac_type)

    # Get converted type
    key = case["hvac_system_type"]
    hvac_type = data_hvac_type[key]

    case_hvac_converted = case
    case_hvac_converted["hvac_system_type"] = hvac_type
    f_hvac_type.close()

    return case_hvac_converted


def get_schedule_by_name(schedules, name):
    """this method takes a dictionary of schedules with names NOT as dict key, searches and return a schedule dict by
        schedule name. Because the actual schedule vectors are hard coded into schedule["periods"]["0"]["day_of_week"],
        we are going to return this for now and this shall be revised in the future

    Args:
        schedules: e.g. proc_case["schedules"]

    Returns:
        dict represent ONE schedule
    """

    for k, v in schedules.items():
        if v["name"].strip().lower() == name.strip().lower():
            # no guard put below because we make strong assumption about the schedule structure.
            # if the assumption is violated, we should let it break and fix it.
            return v["periods"]["0"]["day_of_week"]
    return None
