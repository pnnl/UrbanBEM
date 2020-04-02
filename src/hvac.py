from io import StringIO
from typing import Dict, List
from eppy import modeleditor
from eppy.modeleditor import IDF
from recipes import copy_idf_objects, read_json

IDF.setiddname("../resources/Energy+V9_0_1.idd")


class HVAC:
    """Add HVAC unitary system to zones"""

    hvac_settings = read_json("hvac_settings.json")

    def __init__(self, case: Dict, idf: IDF):
        self.idf = idf
        self.case = case

        # several parameters to be used in different helpers below
        self.economizer_type = (
            "FixedDryBulb" if case["hvac"]["economizer"] else "NoEconomizer"
        )
        self.heat_recovery_type = (
            "Sensible" if case["hvac"]["heat_recovery"] else "None"
        )
        self.oa_name = f"{self.hvac_settings['outdoorair_defaults']['outdoor_air_name_prefix']}{self.case['building_area_type']}"
        self.thermostat_name = self.hvac_settings["thermostat_defaults"]["name"]
        self.system_name_prefix = f"{self.hvac_settings['template_unitary_defaults']['system_name_prefix']}{self.case['building_area_type']}_"

        # run strategy

        self.zone_list = []
        for key, val in self.case["zone_geometry"].items():
            self.zone_list.append({"zone_id": int(key), "zone_name": f"Block {val['name']} Storey 0"}) # TODO: temporarily set per geomeppy naming convention

        self.idf = copy_idf_objects(self.idf, self.add_thermostat())
        for zone in self.zone_list:
            self.idf = copy_idf_objects(self.idf, self.add_zone_hvac(zone))
        self.idf = copy_idf_objects(self.idf, self.add_oa())

    def add_zone_hvac(self, zone_dict: Dict) -> IDF:
        local_idf = IDF(StringIO(""))
        availability_sch_name = self.hvac_settings["hvac_schedule_names"][
            "system_availability_schedule_name"
        ]
        hvaczone_kwargs = {
            "key": "HVACTEMPLATE:ZONE:UNITARY",
            "Zone_Name": zone_dict["zone_name"],
            "Template_Unitary_System_Name": f"{self.system_name_prefix}{str(zone_dict['zone_id'] + 1).zfill(3)}",
            "Template_Thermostat_Name": self.thermostat_name,
            "Zone_Heating_Sizing_Factor": self.hvac_settings[
                "template_unitary_defaults"
            ]["zone_heating_sizing_factor"],
            "Zone_Cooling_Sizing_Factor": self.hvac_settings[
                "template_unitary_defaults"
            ]["zone_cooling_sizing_factor"],
            "Outdoor_Air_Method": "DetailedSpecification",  # hard code because no other choices in the current code
            "Zone_Heating_Design_Supply_Air_Temperature": self.hvac_settings[
                "template_unitary_defaults"
            ]["zone_heating_design_supply_air_temperature"],
            "Design_Specification_Outdoor_Air_Object_Name": self.oa_name,
        }

        local_idf.newidfobject(**hvaczone_kwargs)

        hvacsystem_kwargs = {
            "key": "HVACTEMPLATE:SYSTEM:UNITARYSYSTEM",
            "Name": f"{self.system_name_prefix}{str(zone_dict['zone_id'] + 1).zfill(3)}",
            "System_Availability_Schedule_Name": availability_sch_name,
            "Control_Zone_or_Thermostat_Location_Name": zone_dict["zone_name"],
            "Supply_Fan_Operating_Mode_Schedule_Name": self.hvac_settings[
                "hvac_schedule_names"
            ]["hvac_operation_schedule_name"],
            "Cooling_Coil_Type": self.case["hvac"]["cooling_coil_type"],
            "Cooling_Coil_Availability_Schedule_Name": availability_sch_name,
            "Heating_Coil_Type": self.case["hvac"]["heating_coil_type"],
            "Heating_Coil_Availability_Schedule_Name": availability_sch_name,
            "Heating_Design_Supply_Air_Temperature": self.hvac_settings[
                "template_unitary_defaults"
            ]["heating_design_supply_air_temperature"],
            "Heat_Pump_Heating_Minimum_Outdoor_DryBulb_Temperature": self.hvac_settings[
                "template_unitary_defaults"
            ]["heat_pump_heating_min_outdoor_temp"],
            "Heat_Pump_Defrost_Maximum_Outdoor_DryBulb_Temperature": self.hvac_settings[
                "template_unitary_defaults"
            ]["heat_pump_heating_max_outdoor_temp"],
            "Heat_Pump_Defrost_Control": self.hvac_settings[
                "template_unitary_defaults"
            ]["heat_pump_defrost_control"],
            "Economizer_Type": self.economizer_type,
            "Economizer_Lockout": self.hvac_settings["template_unitary_defaults"][
                "economizer_lockout"
            ],
            "Heat_Recovery_Type": self.heat_recovery_type,
            "Sizing_Option": self.hvac_settings["template_unitary_defaults"][
                "sizing_option"
            ],
        }

        local_idf.newidfobject(**hvacsystem_kwargs)
        return local_idf

    def add_oa(self) -> IDF:
        local_idf = IDF(StringIO(""))
        local_idf.newidfobject(
            "DESIGNSPECIFICATION:OUTDOORAIR",
            Name=self.oa_name,
            Outdoor_Air_Method=self.hvac_settings["outdoorair_defaults"][
                "outdoor_air_method"
            ],
            Outdoor_Air_Flow_per_Person=self.hvac_settings["outdoorair_defaults"][
                "outdoor_air_flow_per_person"
            ],
            Outdoor_Air_Flow_per_Zone_Floor_Area=self.hvac_settings[
                "outdoorair_defaults"
            ]["outdoor_air_flow_per_zone_floor_area"],
        )
        return local_idf

    def add_thermostat(self) -> IDF:
        local_idf = IDF(StringIO(""))
        local_idf.newidfobject(
            "HVACTEMPLATE:THERMOSTAT",
            Name=self.thermostat_name,
            Heating_Setpoint_Schedule_Name=self.hvac_settings["hvac_schedule_names"][
                "heating_setpoint_schedule_name"
            ],
            Cooling_Setpoint_Schedule_Name=self.hvac_settings["hvac_schedule_names"][
                "cooling_setpoint_schedule_name"
            ],
        )
        return local_idf

    def save_idf(self, path):
        self.idf.saveas(path, lineendings="unix")
