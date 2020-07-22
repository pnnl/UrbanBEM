require "openstudio"
require "openstudio-standards"
standard = Standard.build("90.1-2013")
casename = ARGV[0]
idf = OpenStudio::Workspace.load("../hvac_dev/zones_#{casename}.idf").get
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

hvac_system_type = ARGV[1]

case hvac_system_type
when "PSZ_Gas_SingleSpeedDX"
  standard.model_add_hvac_system(osm, "PSZ-AC", "NaturalGas", nil, nil, osm.getThermalZones, hot_water_loop_type: nil, chilled_water_loop_cooling_type: nil, heat_pump_loop_cooling_type: nil, air_loop_heating_type: "Gas", air_loop_cooling_type: nil)
when "PSZ_Electric_SingleSpeedDX"
  standard.model_add_hvac_system(osm, "PSZ-AC", "Electricity", "Electricity", nil, osm.getThermalZones, hot_water_loop_type: nil, chilled_water_loop_cooling_type: nil, heat_pump_loop_cooling_type: nil, air_loop_heating_type: nil, air_loop_cooling_type: nil)
when "VAV_HotWater_ChilledWater"
  names = Array.new()
  floors = Array.new()
  osm.getThermalZones.each do |zone|
    zonename = zone.name
    names.push(zonename.to_s.strip)
    floors.push('Storey ' + zonename.to_s.strip.split(' ')[-3])
  end
  uniquefloors = floors.uniq
  all_zones = osm.getThermalZones
  uniquefloors.sort.each do |floor|
    floorzones = all_zones.select {|z| z.name.to_s.include? floor}
    puts "Adding vav for #{floor}"
    standard.model_add_hvac_system(osm, "VAV Reheat", "NaturalGas", "NaturalGas", nil, floorzones, hot_water_loop_type: "HighTemperature", chilled_water_loop_cooling_type: "AirCooled", heat_pump_loop_cooling_type: nil, air_loop_heating_type: nil, air_loop_cooling_type: "Water")
  end
else
  puts "HVAC system not in the list, ABORT"
end

trans = OpenStudio::EnergyPlus::ForwardTranslator.new
idf = trans.translateModel(osm)
idf.save("../hvac_dev/zones_hvacadded_#{casename}.idf", true)
