from io import StringIO
from typing import Dict
from eppy import modeleditor
from eppy.modeleditor import IDF
from recipes import copy_idf_objects

IDF.setiddname("../resources/V9-5-0-Energy+.idd")


class Overhang:
    def __init__(self, case: Dict, idf: IDF):
        
        self.idf = idf
        self.number_of_floor = int(case["zone_geometry"][0]["num_floors"])
        self.building_area_type = case["building_area_type"]
        overhangflag = False
        
        if case["overhang"]["has_overhang"].lower() == "yes":
            overhangflag = True
        
        self.add_overhang(
            has_overhang = overhangflag
        )

    def set_overhang_objects(self) -> IDF:
        """Set overhang objects"""
        
        local_idf = IDF(StringIO(""))
        
        for floor in range(self.number_of_floor):
            
            window_name_0001 = "Block " + self.building_area_type + "_east_zone Storey " + str(floor) + " Wall 0001 window"
            window_name_0002 = "Block " + self.building_area_type + "_north_zone Storey " + str(floor) + " Wall 0002 window"
            window_name_0003 = "Block " + self.building_area_type + "_west_zone Storey " + str(floor) + " Wall 0003 window"
            window_name_0004 = "Block " + self.building_area_type + "_south_zone Storey " + str(floor) + " Wall 0004 window"
            
            overhang_0001_dict = {
                "key": "SHADING:OVERHANG",
                "Name": window_name_0001 + " overhang",
                "Window_or_Door_Name": window_name_0001,
                "Height_above_Window_or_Door": 0.1,
                "Tilt_Angle_from_WindowDoor": 90,
                "Left_extension_from_WindowDoor_Width": 0,
                "Right_extension_from_WindowDoor_Width": 0,
                "Depth": 0.5,
            }
            
            overhang_0002_dict = {
                "key": "SHADING:OVERHANG",
                "Name": window_name_0002 + " overhang",
                "Window_or_Door_Name": window_name_0002,
                "Height_above_Window_or_Door": 0.1,
                "Tilt_Angle_from_WindowDoor": 90,
                "Left_extension_from_WindowDoor_Width": 0,
                "Right_extension_from_WindowDoor_Width": 0,
                "Depth": 0.5,
            }
            
            overhang_0003_dict = {
                "key": "SHADING:OVERHANG",
                "Name": window_name_0003 + " overhang",
                "Window_or_Door_Name": window_name_0003,
                "Height_above_Window_or_Door": 0.1,
                "Tilt_Angle_from_WindowDoor": 90,
                "Left_extension_from_WindowDoor_Width": 0,
                "Right_extension_from_WindowDoor_Width": 0,
                "Depth": 0.5,
            }
            
            overhang_0004_dict = {
                "key": "SHADING:OVERHANG",
                "Name": window_name_0004 + " overhang",
                "Window_or_Door_Name": window_name_0004,
                "Height_above_Window_or_Door": 0.1,
                "Tilt_Angle_from_WindowDoor": 90,
                "Left_extension_from_WindowDoor_Width": 0,
                "Right_extension_from_WindowDoor_Width": 0,
                "Depth": 0.5,
            }
        
        
            local_idf.newidfobject(**overhang_0001_dict)
            local_idf.newidfobject(**overhang_0002_dict)
            local_idf.newidfobject(**overhang_0003_dict)
            local_idf.newidfobject(**overhang_0004_dict)

        return local_idf

    def add_overhang(self, has_overhang = False) -> IDF:
        """
        Set all overhang ojectcs
        """
        if has_overhang:
            self.idf = copy_idf_objects(self.idf, self.set_overhang_objects())

        return self.idf
    
    
    def save_idf(self, path):
        self.idf.saveas(path, lineendings="unix")