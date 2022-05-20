# HVAC feature Implementation

Jerry Lei
03/30/2022

## DCV in air loop HVAC

This is the same way OSSTD implements DCV

### Applicable Systems

This implementation applies to air loops taht has OA intake (`AIRLOOPHVAC:OUTDOORAIRSYSTEM`)

1. PSZ, Gas, SingleSpeedDX
2. PSZ, Electric, SingleSpeedDX
3. VAV, HotWater, ChilledWater
4. PSZ-HP
5. Packaged VAV, Gas Heating, Electric Reheat
6. VAV with PFP boxes
7. Packaged VAV with Reheat

### objects to be instrumented

```ruby
oa_system = air_loop_hvac.airLoopHVACOutdoorAirSystem.get
controller_oa = oa_system.getControllerOutdoorAir
# Change the min flow rate in the controller outdoor air
controller_oa.setMinimumOutdoorAirFlowRate(0.0)
# Enable DCV in the controller mechanical ventilation
controller_mv.setDemandControlledVentilation(true)
```

## ERV in air loop HVAC

```ruby
if erv_flag == 'true'
  if ["PSZ_Gas_SingleSpeedDX",
      "PSZ_Electric_SingleSpeedDX",
      "VAV_HotWater_ChilledWater",
      "PSZ_HP",
      "PVAV_Gas_ElectricReheat",
      "VAV_PFP",
      "PVAV_Gas_GasReheat"].include? hvac_system_type
    osm.getAirLoopHVACs.each do |air_loop|
      puts "Add ERV for #{air_loop.name}"
      standard.air_loop_hvac_apply_energy_recovery_ventilator(air_loop, nil)
    end
  else
    puts "ERV flag is true, but system type is not applicable."
  end
end
```

## Economizer in air loop HVAC

## Service How Water

```ruby
  # Creates a service water heating loop.
  #
  # @param model [OpenStudio::Model::Model] OpenStudio model object
  # @param system_name [String] the name of the system, or nil in which case it will be defaulted
  # @param water_heater_thermal_zone [OpenStudio::Model::ThermalZone]
  #   zones to place water heater in.  If nil, will be assumed in 70F air for heat loss.
  # @param service_water_temperature [Double] service water temperature, in C
  # @param service_water_pump_head [Double] service water pump head, in Pa
  # @param service_water_pump_motor_efficiency [Double] service water pump motor efficiency, as decimal.
  # @param water_heater_capacity [Double] water heater heating capacity, in W
  # @param water_heater_volume [Double] water heater volume, in m^3
  # @param water_heater_fuel [String] water heater fuel. Valid choices are NaturalGas, Electricity
  # @param parasitic_fuel_consumption_rate [Double] the parasitic fuel consumption rate of the water heater, in W
  # @param add_pipe_losses [Bool] if true, add piping and associated heat losses to system.  If false, add no pipe heat losses
  # @param floor_area_served [Double] area served by the SWH loop, in m^2.  Used for pipe loss piping length estimation
  # @param number_of_stories [Integer] number of stories served by the SWH loop.  Used for pipe loss piping length estimation
  # @param pipe_insulation_thickness [Double] thickness of the fiberglass batt pipe insulation, in m.  Use 0 for uninsulated pipes
  # @param number_water_heaters [Double] the number of water heaters represented by the capacity and volume inputs.
  # Used to modify efficiencies for water heaters based on individual component size while avoiding having to model
  # lots of individual water heaters (for runtime sake).
  # @return [OpenStudio::Model::PlantLoop]
  # the resulting service water loop.
  def model_add_swh_loop(model,
                         system_name,
                         water_heater_thermal_zone,
                         service_water_temperature,
                         service_water_pump_head,
                         service_water_pump_motor_efficiency,
                         water_heater_capacity,
                         water_heater_volume,
                         water_heater_fuel,
                         parasitic_fuel_consumption_rate,
                         add_pipe_losses = false,
                         floor_area_served = 465,
                         number_of_stories = 1,
                         pipe_insulation_thickness = 0.0127, # 1/2in
                         number_water_heaters = 1)
```