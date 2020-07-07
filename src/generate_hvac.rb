require "openstudio"
require "openstudio-standards"
standard = Standard.build("90.1-2013")
idf = OpenStudio::Workspace.load("../hvac_dev/zones.idf").get
trans = OpenStudio::EnergyPlus::ReverseTranslator.new
osm = trans.translateWorkspace(idf)
# model_add_hvac_system(model,
#     system_type,
#     main_heat_fuel,
#     zone_heat_fuel,
#     cool_fuel,
#     zones,
#     hot_water_loop_type: 'HighTemperature',
#     chilled_water_loop_cooling_type: 'WaterCooled',
#     heat_pump_loop_cooling_type: 'EvaporativeFluidCooler',
#     air_loop_heating_type: 'Water',
#     air_loop_cooling_type: 'Water',
#     zone_equipment_ventilation: true,
#     fan_coil_capacity_control_method: 'CyclingFan')

# TODO: For dev purpose. Need refactor for production

# PSZ, Gas, SingleSpeedDX
# standard.model_add_hvac_system(osm, "PSZ-AC", "NaturalGas", nil, nil, osm.getThermalZones, air_loop_heating_type: "Gas")

# VAV, HotWater, ChilledWater
standard.model_add_hvac_system(osm, "VAV Reheat", "NaturalGas", "NaturalGas", nil, osm.getThermalZones, hot_water_loop_type: "HighTemperature", chilled_water_loop_cooling_type: "AirCooled", air_loop_cooling_type: "Water")

# PSZ, Electric, SingleSpeedDX
# standard.model_add_hvac_system(osm, "PSZ-AC", "Electricity", "Electricity", nil, osm.getThermalZones, air_loop_heating_type: nil)

trans = OpenStudio::EnergyPlus::ForwardTranslator.new
idf = trans.translateModel(osm)
idf.save("../hvac_dev/zones_hvacadded.idf", true)
