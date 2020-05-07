require 'openstudio'
require 'openstudio-standards'
standard = Standard.build('90.1-2013')
idf = OpenStudio::Workspace.load("../../hvac_dev/zones.idf").get
trans = OpenStudio::EnergyPlus::ReverseTranslator.new 
osm = trans.translateWorkspace(idf)
trans = OpenStudio::EnergyPlus::ForwardTranslator.new
idf = trans.translateModel(osm)
idf.save('../../hvac_dev/zones_translated.idf', true)