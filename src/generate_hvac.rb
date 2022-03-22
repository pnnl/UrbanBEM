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

names = Array.new()
floors = Array.new()
osm.getThermalZones.each do |zone|
  zonename = zone.name
  names.push(zonename.to_s.strip)
  floors.push('Storey ' + zonename.to_s.strip.split(' ')[-3])
end
uniquefloors = floors.uniq
all_zones = osm.getThermalZones

case hvac_system_type
when "PSZ_Gas_SingleSpeedDX" # CBSA HVAC type 3. PSZ-AC
  puts "Adding #{hvac_system_type} for all zones"
  standard.model_add_hvac_system(osm, "PSZ-AC", "NaturalGas", nil, nil, osm.getThermalZones, hot_water_loop_type: nil, chilled_water_loop_cooling_type: nil, heat_pump_loop_cooling_type: nil, air_loop_heating_type: "Gas", air_loop_cooling_type: nil)
when "PSZ_Electric_SingleSpeedDX"
  puts "Adding #{hvac_system_type} for all zones"
  standard.model_add_hvac_system(osm, "PSZ-AC", "Electricity", "Electricity", nil, osm.getThermalZones, hot_water_loop_type: nil, chilled_water_loop_cooling_type: nil, heat_pump_loop_cooling_type: nil, air_loop_heating_type: nil, air_loop_cooling_type: nil)
when "VAV_HotWater_ChilledWater"
  uniquefloors.sort.each do |floor|
    floorzones = all_zones.select {|z| z.name.to_s.include? floor}
    puts "Adding #{hvac_system_type} for #{floor}"
    standard.model_add_hvac_system(osm, "VAV Reheat", "NaturalGas", "NaturalGas", nil, floorzones, hot_water_loop_type: "HighTemperature", chilled_water_loop_cooling_type: "AirCooled", heat_pump_loop_cooling_type: nil, air_loop_heating_type: nil, air_loop_cooling_type: "Water")
  end
when "Gas_Heating_Ventilation" # CBSA HVAC type 9. Heating and ventilation
  puts "Adding #{hvac_system_type} for all zones"
  standard.model_add_hvac_system(osm, "Unit Heaters", "NaturalGas", nil, nil, osm.getThermalZones)#, hot_water_loop_type: nil, chilled_water_loop_cooling_type: nil, heat_pump_loop_cooling_type: nil, air_loop_heating_type:nil, air_loop_cooling_type: nil, zone_equipment_ventilation: nil, fan_coil_capacity_control_method: nil)
when "PTHP" # CBSA HVAC type 2. PTHP
  uniquefloors.sort.each do |floor|
    floorzones = all_zones.select {|z| z.name.to_s.include? floor}
    puts "Adding #{hvac_system_type} for #{floor}"
    standard.model_add_hvac_system(osm,"PTHP", nil, nil, nil, floorzones)
  end
when "PTAC_Electric" # CBSA HVAC type 1.1 PTAC with electric heating
  uniquefloors.sort.each do |floor|
    floorzones = all_zones.select {|z| z.name.to_s.include? floor}
    puts "Adding #{hvac_system_type} for #{floor}"
    standard.model_add_hvac_system(osm,"PTAC", "Electricity", nil, nil, floorzones)
  end
when "PTAC_Gas" # CBSA HVAC type 1. PTAC
  uniquefloors.sort.each do |floor|
    floorzones = all_zones.select {|z| z.name.to_s.include? floor}
    puts "Adding #{hvac_system_type} for #{floor}"
    standard.model_add_hvac_system(osm,"PTAC", "NaturalGas", nil, nil, floorzones)
  end
when "Electric_Heating_Ventilation" # CBSA HVAC 10. Heating and ventilation
  puts "Adding #{hvac_system_type} for all zones"
  standard.model_add_hvac_system(osm, "Unit Heaters", "Electricity", nil, nil, osm.getThermalZones)
when "PSZ_HP" # CBSA HVAC type 4. PSZ-HP
  puts "Adding #{hvac_system_type} for all zones"
  standard.model_add_hvac_system(osm, "PSZ-HP", nil, nil, nil, osm.getThermalZones)
when "PVAV_Gas_ElectricReheat" # CBSA HVAC type 5.1 Packaged VAV with gas central heating and electric reheat
  uniquefloors.sort.each do |floor|
    floorzones = all_zones.select {|z| z.name.to_s.include? floor}
    puts "Adding #{hvac_system_type} for #{floor}"
    standard.model_add_hvac_system(osm,"PVAV Reheat", "NaturalGas", "Electricity", "Electricity", floorzones, hot_water_loop_type: "HighTemperature")
  end
when "Fan_Coil" # CBSA HVAC type 16. Four-pipe fan-coil
  puts "Adding #{hvac_system_type} for all zones"
  standard.model_add_hvac_system(osm, "Fan Coil", "NaturalGas", nil, "Electricity", osm.getThermalZones, hot_water_loop_type: "HighTemperature", chilled_water_loop_cooling_type: "AirCooled")
when "VAV_PFP" # CBSA HVAC type 8. VAV with PFP boxes
  uniquefloors.sort.each do |floor|
    floorzones = all_zones.select {|z| z.name.to_s.include? floor}
    puts "Adding #{hvac_system_type} for #{floor}"
    standard.model_add_hvac_system(osm, "VAV PFP Boxes", nil, nil, nil, floorzones, hot_water_loop_type: nil, chilled_water_loop_cooling_type: "AirCooled")
  end
when "PVAV_Gas_GasReheat"
  uniquefloors.sort.each do |floor|
    floorzones = all_zones.select {|z| z.name.to_s.include? floor}
    puts "Adding #{hvac_system_type} for #{floor}"
    standard.model_add_hvac_system(osm,"PVAV Reheat", "NaturalGas", "NaturalGas", "Electricity", floorzones, hot_water_loop_type: "HighTemperature")
  end
else
  puts "HVAC system not in the list, ABORT"
end

trans = OpenStudio::EnergyPlus::ForwardTranslator.new
idf = trans.translateModel(osm)
idf.save("../hvac_dev/zones_hvacadded_#{casename}.idf", true)
