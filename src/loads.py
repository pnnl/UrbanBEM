from io import StringIO
from typing import Dict
from eppy import modeleditor
from eppy.modeleditor import IDF
from recipes import copy_idf_objects

IDF.setiddname("../resources/V9-5-0-Energy+.idd")


class Loads:
    def __init__(self, case: Dict, idf: IDF):
        self.idf = idf
        self.building_area_type = case["building_area_type"]
        self.electric_equipment = None
        self.lighting = None
        self.infiltration = None
        self.people = None
        if "electric_equipment" in case["internal_loads"].keys():
            self.electric_equipment = case["internal_loads"]["electric_equipment"]
            eflag = True
        if "gas_equipment" in case["internal_loads"].keys():
            self.gas_equipment = case["internal_loads"]["gas_equipment"]
            gflag = True
        if "lighting" in case["internal_loads"].keys():
            self.lighting = case["internal_loads"]["lighting"]
            lflag = True
        if "infiltration" in case["internal_loads"].keys():
            self.infiltration = case["internal_loads"]["infiltration"]
            iflag = True
        if "people" in case["internal_loads"].keys():
            self.people = case["internal_loads"]["people"]
            pflag = True
        self.set_loads(
            elec_equipment=eflag,
            gas_equipment=gflag,
            lighting=lflag,
            infiltration=iflag,
            people=pflag,
        )

    def set_electric_equipment(self) -> IDF:
        """
        Set electric equipment loads
        """
        local_idf = IDF(StringIO(""))
        eqp = local_idf.newidfobject("ELECTRICEQUIPMENT")
        eqp.Name = "{}_eqp".format(self.building_area_type)
        eqp.Zone_or_ZoneList_Name = "zone_list_{}".format(
            self.building_area_type.strip()
        )
        eqp.Schedule_Name = self.electric_equipment["schedule"]
        eqp.Design_Level_Calculation_Method = "Watts/Area"
        eqp.Watts_per_Zone_Floor_Area = self.electric_equipment["epd"]
        eqp.Fraction_Latent = self.electric_equipment["frac_latent"]
        eqp.Fraction_Radiant = self.electric_equipment["frac_radiant"]
        eqp.Fraction_Lost = self.electric_equipment["frac_lost"]
        return local_idf

    def set_gas_equipment(self) -> IDF:
        """Set gas equipment loads"""
        local_idf = IDF(StringIO(""))
        gas_equipment_obj_dict = {
            "key": "GASEQUIPMENT",
            "Name": f"{self.building_area_type}_gas_equipment",
            "Zone_or_ZoneList_Name": f"Block {self.building_area_type}_north_zone Storey 0",
            "Schedule_Name": self.gas_equipment["schedule"],
            "Design_Level_Calculation_Method": "Watts/Area",
            "Design_Level": self.gas_equipment["watts"],
            "Fraction_Latent": self.gas_equipment["frac_latent"],
            "Fraction_Radiant": self.gas_equipment["frac_radiant"],
            "Fraction_Lost": self.gas_equipment["frac_lost"],
        }
        local_idf.newidfobject(**gas_equipment_obj_dict)
        return local_idf

    def set_lighting(self) -> IDF:
        """
        Set lighting loads
        """
        local_idf = IDF(StringIO(""))
        lgt = local_idf.newidfobject("LIGHTS")
        lgt.Name = "{}_lgt".format(self.building_area_type)
        lgt.Zone_or_ZoneList_Name = "zone_list_{}".format(
            self.building_area_type.strip()
        )
        lgt.Schedule_Name = self.lighting["schedule"]
        lgt.Design_Level_Calculation_Method = "Watts/Area"
        lgt.Watts_per_Zone_Floor_Area = self.lighting["lpd"]
        lgt.Fraction_Radiant = self.lighting["frac_radiant"]
        lgt.Fraction_Visible = self.lighting["frac_visible"]
        return local_idf

    def set_infiltration(self) -> IDF:
        """
        Set infiltration loads
        """
        local_idf = IDF(StringIO(""))
        inf = local_idf.newidfobject("ZONEINFILTRATION:DESIGNFLOWRATE")
        inf.Name = "{}_inf".format(self.building_area_type)
        inf.Zone_or_ZoneList_Name = "zone_list_{}".format(
            self.building_area_type.strip()
        )
        inf.Schedule_Name = self.infiltration["schedule"]
        inf.Design_Flow_Rate_Calculation_Method = "Flow/ExteriorArea"
        inf.Flow_per_Exterior_Surface_Area = self.infiltration["inf"]
        # DOE-2 coefficients
        inf.Constant_Term_Coefficient = 0
        inf.Temperature_Term_Coefficient = 0
        inf.Velocity_Term_Coefficient = 0.224
        inf.Velocity_Squared_Term_Coefficient = 0
        return local_idf

    def set_people(self) -> IDF:
        """
        Set occupants
        """
        local_idf = IDF(StringIO(""))
        ppl = local_idf.newidfobject("PEOPLE")
        ppl.Name = "{}_ppl".format(self.building_area_type)
        ppl.Zone_or_ZoneList_Name = "zone_list_{}".format(
            self.building_area_type.strip()
        )
        ppl.Number_of_People_Schedule_Name = self.people["schedule"]
        ppl.Number_of_People_Calculation_Method = "People/Area"
        ppl.People_per_Zone_Floor_Area = self.people["people"]
        ppl.Fraction_Radiant = self.people["frac_radiant"]
        ppl.Activity_Level_Schedule_Name = self.people["activity_schedule"]
        return local_idf

    def set_loads(
        self,
        elec_equipment=True,
        gas_equipment=True,
        lighting=True,
        infiltration=True,
        people=True,
    ) -> IDF:
        """
        Set all requested loads
        """
        if elec_equipment:
            self.idf = copy_idf_objects(self.idf, self.set_electric_equipment())
        if gas_equipment:
            self.idf = copy_idf_objects(self.idf, self.set_gas_equipment())
        if lighting:
            self.idf = copy_idf_objects(self.idf, self.set_lighting())
        if infiltration:
            self.idf = copy_idf_objects(self.idf, self.set_infiltration())
        if people:
            self.idf = copy_idf_objects(self.idf, self.set_people())

        return self.idf

    def save_idf(self, path):
        self.idf.saveas(path, lineendings="unix")
