require "openstudio"
require "openstudio-standards"
standard = Standard.build("90.1-2013")
casename = '3306'#ARGV[0]
idf = OpenStudio::Workspace.load("../hvac_dev/zones_#{casename}.idf").get
trans = OpenStudio::EnergyPlus::ReverseTranslator.new
osm = trans.translateWorkspace(idf)

# below is from midrise apartment
prototype_input_hash = { 
    "main_water_heater_volume" => 1150, # autosize
    "main_water_heater_space_name" => nil,
    "main_water_heater_fuel" => "Electricity", # std_input
    "main_service_water_temperature" => 140, # assumption
    "main_service_water_pump_head" => 0.01, # assumption
    "main_service_water_pump_motor_efficiency" => 1.0, # assumption
    "main_water_heater_capacity" => 1150000, # autosize
    "main_service_water_parasitic_fuel_consumption_rate" => 6445.536238, # assumption to be determined
    "main_service_water_peak_flowrate" => 1, # assumption tbd
    "main_service_water_flowrate_schedule" => "default", # based on zone occ schedule
    "main_water_use_temperature" => 140,
    "booster_water_heater_volume" => nil, # leave as is
    "laundry_water_heater_volume" => nil # leave as is
 }

standard.model_add_swh(osm, nil, prototype_input_hash)

trans = OpenStudio::EnergyPlus::ForwardTranslator.new
idf = trans.translateModel(osm)
idf.save("../hvac_dev/zones_swhadded_#{casename}.idf", true)