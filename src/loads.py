from io import StringIO
from typing import Dict
from eppy import modeleditor
from eppy.modeleditor import IDF
from recipes import copy_idf_objects

IDF.setiddname("../resources/Energy+V9_0_1.idd")


class Loads:
    def __init__(self, case: Dict, idf: IDF):
        self.idf = idf
        self.electric_equipment = case["internal_loads"]["electric_equipment"]
        self.lighting = case["internal_loads"]["lighting"]
        self.infiltration = case["internal_loads"]["infiltration"]
        self.people = case["internal_loads"]["people"]
        self.zones = []
        # Retrieves a triple with the zone id, zone name and zone name in idf
        for i, zn in case["zone_geometry"].items():
            for zn_idf in idf.idfobjects["ZONE"]:
                zn_idf_name = zn_idf.Name
                if zn["name"] in zn_idf_name:
                    self.zones.append((i, zn["name"], zn_idf_name))

    def set_electric_equipment(self) -> IDF:
        """
        Set electric equipment loads
        """
        local_idf = IDF(StringIO(""))
        for zn, zn_name, zn_idf_name in self.zones:
            eqp = local_idf.newidfobject("ELECTRICEQUIPMENT")
            eqp.Name = "{}_eqp".format(zn_name)
            eqp.Zone_or_ZoneList_Name = zn_idf_name
            eqp.Design_Level_Calculation_Method = "Watts/Area"
            eqp.Watts_per_Zone_Floor_Area = self.electric_equipment[zn]["epd"]
            eqp.Fraction_Latent = self.electric_equipment[zn]["frac_latent"]
            eqp.Fraction_Radiant = self.electric_equipment[zn]["frac_radiant"]
            eqp.Fraction_Lost = self.electric_equipment[zn]["frac_lost"]
        return local_idf

    def set_lighting(self) -> IDF:
        """
        Set lighting loads
        """
        local_idf = IDF(StringIO(""))
        for zn, zn_name, zn_idf_name in self.zones:
            lgt = local_idf.newidfobject("LIGHTS")
            lgt.Name = "{}_lgt".format(zn_name)
            lgt.Zone_or_ZoneList_Name = zn_idf_name
            lgt.Design_Level_Calculation_Method = "Watts/Area"
            lgt.Watts_per_Zone_Floor_Area = self.lighting[zn]["lpd"]
            lgt.Fraction_Radiant = self.lighting[zn]["frac_radiant"]
            lgt.Fraction_Visible = self.lighting[zn]["frac_visible"]
        return local_idf

    def set_infiltration(self) -> IDF:
        """
        Set infiltration loads
        """
        local_idf = IDF(StringIO(""))
        for zn, zn_name, zn_idf_name in self.zones:
            inf = local_idf.newidfobject("ZONEINFILTRATION:DESIGNFLOWRATE")
            inf.Name = "{}_inf".format(zn_name)
            inf.Zone_or_ZoneList_Name = zn_idf_name
            inf.Design_Flow_Rate_Calculation_Method = "Flow/ExteriorArea"
            inf.Flow_per_Exterior_Surface_Area = self.infiltration[zn]["inf"]
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
        for zn, zn_name, zn_idf_name in self.zones:
            ppl = local_idf.newidfobject("PEOPLE")
            ppl.Name = "{}_ppl".format(zn_name)
            ppl.Zone_or_ZoneList_Name = zn_idf_name
            ppl.Number_of_People_Calculation_Method = "People/Area"
            ppl.People_per_Zone_Floor_Area = self.people[zn]["people"]
            ppl.Fraction_Radiant = self.people[zn]["frac_radiant"]
        return local_idf

    def set_loads(self, equipment=True, lighting=True, infiltration=True, people=True) -> IDF:
        """
        Set all requested loads
        """
        if equipment:
            self.idf = copy_idf_objects(self.idf, self.set_electric_equipment())
        if lighting:
            self.idf = copy_idf_objects(self.idf, self.set_lighting())
        if infiltration:
            self.idf = copy_idf_objects(self.idf, self.set_infiltration())
        if people:
            self.idf = copy_idf_objects(self.idf, self.set_people())

        return self.idf
