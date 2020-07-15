require "openstudio"
require "openstudio-standards"
standard = Standard.build("90.1-2013")
casename = ARGV.pop()
idf = OpenStudio::Workspace.load("../hvac_dev/zones_#{casename}.idf").get
trans = OpenStudio::EnergyPlus::ReverseTranslator.new
osm = trans.translateWorkspace(idf)
<<<<<<< Updated upstream
standard.model_add_hvac_system(osm, "PSZ-AC", "NaturalGas", nil, nil, osm.getThermalZones, air_loop_heating_type: "Gas")
=======
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

# PSZ:AC 
standard.model_add_hvac_system(osm, "PSZ-AC", "NaturalGas", nil, nil, osm.getThermalZones, air_loop_heating_type: "Gas")

# PSZ:HP
# standard.model_add_hvac_system(osm, "PSZ-HP", nil, nil, nil, osm.getThermalZones)

# Multi-zone VAV with elec reheat
# standard.model_add_hvac_system(osm, "VAV Reheat", "NaturalGas", "Electricity", nil, osm.getThermalZones)

# PSZ:
>>>>>>> Stashed changes
trans = OpenStudio::EnergyPlus::ForwardTranslator.new
idf = trans.translateModel(osm)
idf.save("../hvac_dev/zones_hvacadded_#{casename}.idf", true)
