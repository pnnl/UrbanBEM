from io import StringIO
from typing import Dict
from eppy import modeleditor
from eppy.modeleditor import IDF
from recipes import copy_idf_objects

IDF.setiddname("../resources/V9-5-0-Energy+.idd")


class Photovoltaic:
    def __init__(self, case: Dict, idf: IDF):
        
        self.idf = idf
        pv_power_density = 0.25*10.7639 # Assuming 0.25 W/ft2 of total floor area
        pvflag = False
        
        if case["pv"]["has_rooftop_pv"].lower() == "yes":
            pvflag = True
            self.pv_capacity = case["pv"]["rooftop_pv_area"]*pv_power_density
        
        self.add_pv(
            has_pv = pvflag
        )

    def set_pv_objects(self) -> IDF:
        """Set pv related objects"""
        local_idf = IDF(StringIO(""))
        pvwatts_obj_dict = {
            "key": "GENERATOR:PVWATTS",
            "Name": "PV_module",
            "PVWatts_Version": "",
            "DC_System_Capacity": self.pv_capacity,
            "Module_Type": "Standard",  
            "Array_Type": "FixedRoofMounted",
            "System_Losses": 0.113,
            "Array_Geometry_Type": "TiltAzimuth", 
            "Tilt_Angle": 45.0,
            "Azimuth_Angle": 180.0,
            "Surface_Name": "",
            "Ground_Coverage_Ratio":"",
        }
        
        generator_obj_dict = {
            "key": "ELECTRICLOADCENTER:GENERATORS",
            "Name": "PV_Generator",
            "Generator_1_Name": "PV_module",
            "Generator_1_Object_Type": "Generator:PVWatts",
            "Generator_1_Rated_Electric_Power_Output": self.pv_capacity,
            "Generator_1_Availability_Schedule_Name": "always_on",
            "Generator_1_Rated_Thermal_to_Electrical_Power_Ratio": "",
        }

        inverter_obj_dict = {
            "key": "ELECTRICLOADCENTER:INVERTER:PVWATTS",
            "Name": "PV_Inverter",
            "DC_to_AC_Size_Ratio": 1.2,
            "Inverter_Efficiency": 0.96,
        }

        distribution_obj_dict = {
            "key": "ELECTRICLOADCENTER:DISTRIBUTION",
            "Name": "Generator",
            "Generator_List_Name": "PV_Generator",
            "Generator_Operation_Scheme_Type": "Baseload",
            "Generator_Demand_Limit_Scheme_Purchased_Electric_Demand_Limit": "",
            "Generator_Track_Schedule_Name_Scheme_Schedule_Name": "",
            "Generator_Track_Meter_Scheme_Meter_Name": "",
            "Electrical_Buss_Type": "DirectCurrentWithInverter",
            "Inverter_Name": "PV_Inverter",
        }

        local_idf.newidfobject(**pvwatts_obj_dict)
        local_idf.newidfobject(**generator_obj_dict)
        local_idf.newidfobject(**inverter_obj_dict)
        local_idf.newidfobject(**distribution_obj_dict)

        return local_idf

    def add_pv(self, has_pv = False) -> IDF:
        """
        Set all pv ojectcs
        """
        if has_pv:
            self.idf = copy_idf_objects(self.idf, self.set_pv_objects())

        return self.idf
    
    
    def save_idf(self, path):
        self.idf.saveas(path, lineendings="unix")