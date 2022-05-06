require 'openstudio'
require 'openstudio-standards'
require 'json'

casename = ARGV[0] # '3306'
swh_fuel = ARGV[1] # 'Electricity'
main_service_water_peak_flowrate_m3_s = ARGV[2]
code_version = ARGV[3] # '90.1-2013' #

swh_setting_path = './swh_settings.json'
swh_settings = JSON.parse(File.read(swh_setting_path))

idf = OpenStudio::Workspace.load("../#{swh_settings['swh_intermediate_folder_name']}/zones_#{casename}.idf").get
trans = OpenStudio::EnergyPlus::ReverseTranslator.new
osm = trans.translateWorkspace(idf)
standard = Standard.build(code_version)

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
                                peak_flowrate = main_service_water_peak_flowrate_m3_s.to_f,
                                flowrate_schedule = 'default', # TODO: create new one from occ schedule logic, occ x 0.5 without lunch time
                                water_use_temperature = OpenStudio.convert(swh_settings['main_water_use_temperature_F'], 'F', 'C').get,
                                space_name = nil)

osm.getWaterHeaterMixeds.each do |waterheater|
  waterheater.setName('Service Water Heater')
  waterheater.autosize
  waterheater_sizing = waterheater.waterHeaterSizing
  waterheater_sizing.setTimeforTankRecovery(1.5)
end

trans = OpenStudio::EnergyPlus::ForwardTranslator.new
idf = trans.translateModel(osm)
idf.save("../swh_dev/zones_swhadded_#{casename}.idf", true)
