require 'openstudio'
require 'openstudio-standards'
require 'json'

casename = ARGV[0] # '3306'
swh_fuel = ARGV[1] # 'Electricity'
code_version = ARGV[2] # '90.1-2013' # 

idf = OpenStudio::Workspace.load("../#{swh_dev['swh_intermediate_folder_name']}/zones_#{casename}.idf").get
trans = OpenStudio::EnergyPlus::ReverseTranslator.new
osm = trans.translateWorkspace(idf)
standard = Standard.build(code_version)
swh_setting_path = './swh_settings.json'

swh_settings = JSON.parse(File.read(swh_setting_path))
# read settings directly from configuration file

puts swh_settings

# process settings
puts 'Reading service water heating setting'
autosize_placeholder_val = swh_settings['placeholder_value_for_autosize']
swh_settings.each do |k, v|
  swh_settings[k] = autosize_placeholder_val if v == 'autosize'
end

puts 'Adding service water heating'
# create main service water loop

puts 'Adding main service water loop'
main_swh_loop = standard.model_add_swh_loop(model = osm,
                                            system_name = 'Main Service Water Loop',
                                            water_heater_thermal_zone = nil,
                                            service_water_temperature = OpenStudio.convert(swh_settings['main_service_water_temperature_F'], 'F', 'C').get,
                                            service_water_pump_head = swh_settings['main_service_water_pump_head_Pa'],
                                            service_water_pump_motor_efficiency = swh_settings['main_service_water_pump_motor_efficiency'],
                                            water_heater_capacity = swh_settings['main_water_heater_capacity_btu_hr'],
                                            water_heater_volume = swh_settings['main_water_heater_volume_gal'],
                                            water_heater_fuel = swh_fuel,
                                            parasitic_fuel_consumption_rate = OpenStudio.convert(swh_settings['main_service_water_parasitic_fuel_consumption_rate_btu_hr'], 'Btu/hr', 'W').get)

puts 'Adding service hot water end uses'
standard.model_add_swh_end_uses(model = osm,
                                use_name = 'Main',
                                swh_loop = main_swh_loop,
                                peak_flowrate = OpenStudio.convert(swh_settings['main_service_water_peak_flowrate_gal_min'], 'gal/min', 'm^3/s').get,
                                flowrate_schedule = 'default',
                                water_use_temperature = OpenStudio.convert(swh_settings['main_water_use_temperature_F'], 'F', 'C').get,
                                space_name = nil)

osm.getWaterHeaterMixeds.each do |waterheater|
  waterheater.setName('Service Water Heater')
end

# "default_value_for_autosize_gal": 1988,
#   "main_water_heater_capacity_btu_hr": "autosize",
#   "main_water_heater_volume": "autosize",
#   "main_service_water_temperature_F": 140,
#   "main_water_use_temperature_F": 140,
#   "main_service_water_pump_head": 0.01,
#   "main_service_water_pump_motor_efficiency": 1,
#   "main_service_water_parasitic_fuel_consumption_rate_btu_hr": 6400,
#   "main_service_water_peak_flowrate_gal_min": 1
# }

# # below is from midrise apartment
# prototype_input_hash = {
#     "main_water_heater_volume" => 1150, # autosize
#     "main_water_heater_space_name" => nil,
#     "main_water_heater_fuel" => "Electricity", # std_input
#     "main_service_water_temperature" => 140, # assumption
#     "main_service_water_pump_head" => 0.01, # assumption
#     "main_service_water_pump_motor_efficiency" => 1.0, # assumption
#     "main_water_heater_capacity" => 1150000, # autosize
#     "main_service_water_parasitic_fuel_consumption_rate" => 6445.536238, # assumption to be determined
#     "main_service_water_peak_flowrate" => 1, # assumption tbd
#     "main_service_water_flowrate_schedule" => "default", # based on zone occ schedule
#     "main_water_use_temperature" => 140,
#     "booster_water_heater_volume" => nil, # leave as is
#     "laundry_water_heater_volume" => nil # leave as is
#  }

# standard.model_add_swh(osm, nil, prototype_input_hash)

trans = OpenStudio::EnergyPlus::ForwardTranslator.new
idf = trans.translateModel(osm)
idf.save("../hvac_dev/zones_swhadded_#{casename}.idf", true)
