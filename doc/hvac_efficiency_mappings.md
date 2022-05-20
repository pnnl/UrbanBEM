## Fan

### Possible object types in IDF

- FAN:CONSTANTVOLUME
- FAN:VARIABLEVOLUME
- FAN:ONOFF

### object types in OSSTD that is not reachable by UrbanBEM OSSTD calls

- FAN:ZONEEXHAUST (no setting motor efficiciency for this in OSSTD)

### Fields for efficiency

- FanEfficiency
- MotorEfficiency


## Pump

### Possible object types in IDF

- PUMP:VARIABLESPEED

### object types in OSSTD that is not reachable by UrbanBEM OSSTD calls

- PUMP:CONSTANTSPEED
- HEADEREDPUMPS:CONSTANTSPEED
- HEADEREDPUMPS:VARIABLESPEED


### Fields for efficiency

- MotorEfficiency

## Unitary HP DX heating coil

### Possible object types in IDF

- COIL:HEATING:DX:SINGLESPEED

### object types in OSSTD that is not reachable by UrbanBEM OSSTD calls

NA

### Fields for efficiency

- RatedCOP

## Unitary HP DX Cooling coil

### Possible object types in IDF

- COIL:COOLING:DX:SINGLESPEED
- COIL:COOLING:DX:TWOSPEED

### object types in OSSTD that is not reachable by UrbanBEM OSSTD calls

- COIL:COOLING:DX:MULTISPEED

### Fields for efficiency

- COIL:COOLING:DX:TWOSPEED
  - RatedHighSpeedCOP
  - RatedLowSpeedCOP
- COIL:COOLING:DX:SINGLESPEED
  - RatedCOP
- COIL:COOLING:DX:MULTISPEED
```ruby
unless cop.nil?
    clg_stages.each do |istage|
        istage.setGrossRatedCoolingCOP(cop)
    end
end
```
## WSHP (NA)

## Chiller

### Possible object types in IDF

- CHILLER:ELECTRIC:EIR

### object types in OSSTD that is not reachable by UrbanBEM OSSTD calls

NA

### Fields for efficiency

- ReferenceCOP

## Boiler

### Possible object types in IDF

- BOILER:HOTWATER


### object types in OSSTD that is not reachable by UrbanBEM OSSTD calls

NA

### Fields for efficiency

- NominalThermalEfficiency

## Water Heater (used in SWH in UrbanBEM)

### Possible object types in IDF

- WATERHEATER:MIXED

### object types in OSSTD that is not reachable by UrbanBEM OSSTD calls

NA

### Fields for efficiency

- HeaterThermalEfficiency
- Note: Other fields are set in `water_heater_mixed_apply_efficiency`
```ruby
# Skin loss
water_heater_mixed.setOffCycleLossCoefficienttoAmbientTemperature(ua_btu_per_hr_per_c)
water_heater_mixed.setOnCycleLossCoefficienttoAmbientTemperature(ua_btu_per_hr_per_c)
# @todo Parasitic loss (pilot light)
# PNNL document says pilot lights were removed, but IDFs
# still have the on/off cycle parasitic fuel consumptions filled in
water_heater_mixed.setOnCycleParasiticFuelType(fuel_type)
# self.setOffCycleParasiticFuelConsumptionRate(??)
water_heater_mixed.setOnCycleParasiticHeatFractiontoTank(0)
water_heater_mixed.setOffCycleParasiticFuelType(fuel_type)
# self.setOffCycleParasiticFuelConsumptionRate(??)
water_heater_mixed.setOffCycleParasiticHeatFractiontoTank(0)
```

## Cooling tower (NA)

## Fluid cooler (NA)

## Gas Heating Coil

### Possible object types in IDF

- COIL:HEATING:FUEL

### object types in OSSTD that is not reachable by UrbanBEM OSSTD calls

- COIL:HEATING:GAS:MULTISTAGE

### Fields for efficiency

- GasBurnerEfficiency
