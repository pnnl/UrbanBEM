# Object type deltas for OSSTD hvac call

Jerry Lei
03/21/2022

- [Object type deltas for OSSTD hvac call](#object-type-deltas-for-osstd-hvac-call)
  - [Original objects counts](#original-objects-counts)
    - [OSSTD input](#osstd-input)
    - [OSSTD direct translate](#osstd-direct-translate)
  - [PSZ, Gas, SingleSpeedDX](#psz-gas-singlespeeddx)
    - [Ruby call](#ruby-call)
    - [Objects after the call](#objects-after-the-call)
  - [PSZ, Electric, SingleSpeedDX](#psz-electric-singlespeeddx)
    - [Ruby call](#ruby-call-1)
    - [Objects after the call](#objects-after-the-call-1)
  - [VAV, HotWater, ChilledWater](#vav-hotwater-chilledwater)
    - [Ruby call](#ruby-call-2)
    - [Objects after the call](#objects-after-the-call-2)
  - [Heating and Ventilation, Gas](#heating-and-ventilation-gas)
    - [Ruby call](#ruby-call-3)
    - [Objects after the call](#objects-after-the-call-3)
  - [PTHP](#pthp)
    - [Ruby call](#ruby-call-4)
    - [Objects after the call](#objects-after-the-call-4)
  - [PTAC, Electric](#ptac-electric)
    - [Ruby call](#ruby-call-5)
    - [Objects after the call](#objects-after-the-call-5)
  - [PTAC, Gas](#ptac-gas)
    - [Ruby call](#ruby-call-6)
    - [Objects after the call](#objects-after-the-call-6)
  - [Heating and Ventilation, Electric](#heating-and-ventilation-electric)
    - [Ruby call](#ruby-call-7)
    - [Objects after the call](#objects-after-the-call-7)
  - [PSZ-HP](#psz-hp)
    - [Ruby call](#ruby-call-8)
    - [Objects after the call](#objects-after-the-call-8)
  - [Packaged VAV, Gas Heating, Electric Reheat](#packaged-vav-gas-heating-electric-reheat)
    - [Ruby call](#ruby-call-9)
    - [Objects after the call](#objects-after-the-call-9)
  - [WSHP (ignored)](#wshp-ignored)
    - [Ruby call](#ruby-call-10)
    - [Objects after the call](#objects-after-the-call-10)
  - [Four-Pipe Fan-Coil](#four-pipe-fan-coil)
    - [Ruby call](#ruby-call-11)
    - [Objects after the call](#objects-after-the-call-11)
  - [VAV with PFP boxes](#vav-with-pfp-boxes)
    - [Ruby call](#ruby-call-12)
    - [Objects after the call](#objects-after-the-call-12)
  - [Packaged VAV with Reheat](#packaged-vav-with-reheat)
    - [Ruby call](#ruby-call-13)
    - [Objects after the call](#objects-after-the-call-13)

## Original objects counts

### OSSTD input

```
BUILDING: 1
GLOBALGEOMETRYRULES: 1
SIZINGPERIOD:DESIGNDAY: 2
ZONE: 4
Total number of objects: 8
```
note: no difference caused by version upgrade

### OSSTD direct translate

```
BUILDING: 1
GLOBALGEOMETRYRULES: 1
LIFECYCLECOST:NONRECURRINGCOST: 1
LIFECYCLECOST:PARAMETERS: 1
LIFECYCLECOST:USEPRICEESCALATION: 5
OUTDOORAIR:NODE: 1
OUTPUT:SQLITE: 1
OUTPUT:TABLE:SUMMARYREPORTS: 1
OUTPUT:VARIABLEDICTIONARY: 1
OUTPUTCONTROL:TABLE:STYLE: 1
RUNPERIOD: 1
SCHEDULE:CONSTANT: 3
SIMULATIONCONTROL: 1
SIZING:PARAMETERS: 1
SIZINGPERIOD:DESIGNDAY: 2
TIMESTEP: 1
VERSION: 1
ZONE: 4
Total number of objects: 28
```
note: version upgrade causes difference: two `SIZINGPERIOD:DESIGNDAY` added
## PSZ, Gas, SingleSpeedDX

### Ruby call

```ruby
# PSZ, Gas, SingleSpeedDX
standard.model_add_hvac_system(osm, "PSZ-AC", "NaturalGas", nil, nil, osm.getThermalZones, air_loop_heating_type: "Gas")
```

### Objects after the call

```
(BEFORE VERSION UPGRADE)
VERSION: 1
SIMULATIONCONTROL: 1
BUILDING: 1
TIMESTEP: 1
SIZINGPERIOD:DESIGNDAY: 2
RUNPERIOD: 1
SCHEDULETYPELIMITS: 1
SCHEDULE:CONSTANT: 3
GLOBALGEOMETRYRULES: 1
ZONE: 4
DESIGNSPECIFICATION:ZONEAIRDISTRIBUTION: 4
SIZING:PARAMETERS: 1
SIZING:ZONE: 4
SIZING:SYSTEM: 4
AIRTERMINAL:SINGLEDUCT:CONSTANTVOLUME:NOREHEAT: 4
ZONEHVAC:AIRDISTRIBUTIONUNIT: 4
ZONEHVAC:EQUIPMENTLIST: 4
ZONEHVAC:EQUIPMENTCONNECTIONS: 4
FAN:CONSTANTVOLUME: 4
COIL:COOLING:DX:SINGLESPEED: 4
COIL:HEATING:ELECTRIC: 4
COIL:HEATING:FUEL: 4
COILSYSTEM:COOLING:DX: 4
CONTROLLER:OUTDOORAIR: 4
CONTROLLER:MECHANICALVENTILATION: 4
AIRLOOPHVAC:CONTROLLERLIST: 4
AIRLOOPHVAC: 4
AIRLOOPHVAC:OUTDOORAIRSYSTEM:EQUIPMENTLIST: 4
AIRLOOPHVAC:OUTDOORAIRSYSTEM: 4
OUTDOORAIR:MIXER: 4
AIRLOOPHVAC:ZONESPLITTER: 4
AIRLOOPHVAC:SUPPLYPATH: 4
AIRLOOPHVAC:ZONEMIXER: 4
AIRLOOPHVAC:RETURNPATH: 4
BRANCH: 4
BRANCHLIST: 4
NODELIST: 16
OUTDOORAIR:NODE: 1
OUTDOORAIR:NODELIST: 4
AVAILABILITYMANAGER:SCHEDULED: 4
AVAILABILITYMANAGER:NIGHTCYCLE: 4
AVAILABILITYMANAGERASSIGNMENTLIST: 8
SETPOINTMANAGER:SINGLEZONE:REHEAT: 4
SETPOINTMANAGER:MIXEDAIR: 16
CURVE:QUADRATIC: 24
CURVE:BIQUADRATIC: 16
LIFECYCLECOST:PARAMETERS: 1
LIFECYCLECOST:NONRECURRINGCOST: 1
LIFECYCLECOST:USEPRICEESCALATION: 5
OUTPUT:VARIABLEDICTIONARY: 1
OUTPUT:TABLE:SUMMARYREPORTS: 1
OUTPUTCONTROL:TABLE:STYLE: 1
OUTPUT:SQLITE: 1
Total number of objects: 225
```

## PSZ, Electric, SingleSpeedDX

### Ruby call

```ruby
# PSZ, Electric, SingleSpeedDX
standard.model_add_hvac_system(osm, "PSZ-AC", "Electricity", "Electricity", nil, osm.getThermalZones, air_loop_heating_type: nil)
```

### Objects after the call

```
(BEFORE VERSION UPGRADE)
VERSION: 1
SIMULATIONCONTROL: 1
BUILDING: 1
TIMESTEP: 1
SIZINGPERIOD:DESIGNDAY: 2
RUNPERIOD: 1
SCHEDULETYPELIMITS: 1
SCHEDULE:CONSTANT: 3
GLOBALGEOMETRYRULES: 1
ZONE: 4
DESIGNSPECIFICATION:ZONEAIRDISTRIBUTION: 4
SIZING:PARAMETERS: 1
SIZING:ZONE: 4
SIZING:SYSTEM: 4
AIRTERMINAL:SINGLEDUCT:CONSTANTVOLUME:NOREHEAT: 4
ZONEHVAC:AIRDISTRIBUTIONUNIT: 4
ZONEHVAC:EQUIPMENTLIST: 4
ZONEHVAC:EQUIPMENTCONNECTIONS: 4
FAN:CONSTANTVOLUME: 4
COIL:COOLING:DX:SINGLESPEED: 4
COIL:HEATING:ELECTRIC: 8
COILSYSTEM:COOLING:DX: 4
CONTROLLER:OUTDOORAIR: 4
CONTROLLER:MECHANICALVENTILATION: 4
AIRLOOPHVAC:CONTROLLERLIST: 4
AIRLOOPHVAC: 4
AIRLOOPHVAC:OUTDOORAIRSYSTEM:EQUIPMENTLIST: 4
AIRLOOPHVAC:OUTDOORAIRSYSTEM: 4
OUTDOORAIR:MIXER: 4
AIRLOOPHVAC:ZONESPLITTER: 4
AIRLOOPHVAC:SUPPLYPATH: 4
AIRLOOPHVAC:ZONEMIXER: 4
AIRLOOPHVAC:RETURNPATH: 4
BRANCH: 4
BRANCHLIST: 4
NODELIST: 16
OUTDOORAIR:NODE: 1
OUTDOORAIR:NODELIST: 4
AVAILABILITYMANAGER:SCHEDULED: 4
AVAILABILITYMANAGER:NIGHTCYCLE: 4
AVAILABILITYMANAGERASSIGNMENTLIST: 8
SETPOINTMANAGER:SINGLEZONE:REHEAT: 4
SETPOINTMANAGER:MIXEDAIR: 16
CURVE:QUADRATIC: 24
CURVE:BIQUADRATIC: 16
LIFECYCLECOST:PARAMETERS: 1
LIFECYCLECOST:NONRECURRINGCOST: 1
LIFECYCLECOST:USEPRICEESCALATION: 5
OUTPUT:VARIABLEDICTIONARY: 1
OUTPUT:TABLE:SUMMARYREPORTS: 1
OUTPUTCONTROL:TABLE:STYLE: 1
OUTPUT:SQLITE: 1
Total number of objects: 225
```

## VAV, HotWater, ChilledWater

Note: the updated VAV call use zones on one floor, not all zones. Below is for all zones.

### Ruby call

```ruby
# VAV, HotWater, ChilledWater
standard.model_add_hvac_system(osm, "VAV Reheat", "NaturalGas", "NaturalGas", nil, osm.getThermalZones, hot_water_loop_type: "HighTemperature", chilled_water_loop_cooling_type: "AirCooled", air_loop_cooling_type: "Water")
```

### Objects after the call

```
(BEFORE VERSION UPGRADE)
VERSION: 1
SIMULATIONCONTROL: 1
BUILDING: 1
TIMESTEP: 1
SIZINGPERIOD:DESIGNDAY: 2
RUNPERIOD: 1
SCHEDULETYPELIMITS: 2
SCHEDULE:DAY:INTERVAL: 2
SCHEDULE:WEEK:DAILY: 2
SCHEDULE:YEAR: 2
SCHEDULE:CONSTANT: 3
GLOBALGEOMETRYRULES: 1
ZONE: 4
DESIGNSPECIFICATION:ZONEAIRDISTRIBUTION: 4
SIZING:PARAMETERS: 1
SIZING:ZONE: 4
SIZING:SYSTEM: 1
SIZING:PLANT: 1
AIRTERMINAL:SINGLEDUCT:VAV:REHEAT: 4
ZONEHVAC:AIRDISTRIBUTIONUNIT: 4
ZONEHVAC:EQUIPMENTLIST: 4
ZONEHVAC:EQUIPMENTCONNECTIONS: 4
FAN:VARIABLEVOLUME: 1
COIL:COOLING:DX:TWOSPEED: 1
COIL:HEATING:WATER: 5
COILSYSTEM:COOLING:DX: 1
CONTROLLER:WATERCOIL: 1
CONTROLLER:OUTDOORAIR: 1
CONTROLLER:MECHANICALVENTILATION: 1
AIRLOOPHVAC:CONTROLLERLIST: 2
AIRLOOPHVAC: 1
AIRLOOPHVAC:OUTDOORAIRSYSTEM:EQUIPMENTLIST: 1
AIRLOOPHVAC:OUTDOORAIRSYSTEM: 1
OUTDOORAIR:MIXER: 1
AIRLOOPHVAC:ZONESPLITTER: 1
AIRLOOPHVAC:SUPPLYPATH: 1
AIRLOOPHVAC:ZONEMIXER: 1
AIRLOOPHVAC:RETURNPATH: 1
BRANCH: 14
BRANCHLIST: 3
CONNECTOR:SPLITTER: 2
CONNECTOR:MIXER: 2
CONNECTORLIST: 2
NODELIST: 10
OUTDOORAIR:NODE: 1
OUTDOORAIR:NODELIST: 1
PIPE:ADIABATIC: 6
PUMP:VARIABLESPEED: 1
BOILER:HOTWATER: 1
PLANTLOOP: 1
PLANTEQUIPMENTLIST: 1
PLANTEQUIPMENTOPERATION:HEATINGLOAD: 1
PLANTEQUIPMENTOPERATIONSCHEMES: 1
AVAILABILITYMANAGER:SCHEDULED: 1
AVAILABILITYMANAGER:NIGHTCYCLE: 1
AVAILABILITYMANAGERASSIGNMENTLIST: 2
SETPOINTMANAGER:SCHEDULED: 2
SETPOINTMANAGER:MIXEDAIR: 3
CURVE:QUADRATIC: 3
CURVE:BIQUADRATIC: 4
LIFECYCLECOST:PARAMETERS: 1
LIFECYCLECOST:NONRECURRINGCOST: 1
LIFECYCLECOST:USEPRICEESCALATION: 5
OUTPUT:VARIABLEDICTIONARY: 1
OUTPUT:TABLE:SUMMARYREPORTS: 1
OUTPUTCONTROL:TABLE:STYLE: 1
OUTPUT:SQLITE: 1
Total number of objects: 145
```


## Heating and Ventilation, Gas

### Ruby call

```ruby
standard.model_add_hvac_system(osm, "Unit Heaters", "NaturalGas", nil, nil, osm.getThermalZones)
```
### Objects after the call

```
BUILDING: 1
COIL:HEATING:FUEL: 4
FAN:CONSTANTVOLUME: 4
GLOBALGEOMETRYRULES: 1
LIFECYCLECOST:NONRECURRINGCOST: 1
LIFECYCLECOST:PARAMETERS: 1
LIFECYCLECOST:USEPRICEESCALATION: 5
NODELIST: 8
OUTDOORAIR:NODE: 1
OUTPUT:SQLITE: 1
OUTPUT:TABLE:SUMMARYREPORTS: 1
OUTPUT:VARIABLEDICTIONARY: 1
OUTPUTCONTROL:TABLE:STYLE: 1
RUNPERIOD: 1
SCHEDULE:CONSTANT: 3
SCHEDULETYPELIMITS: 1
SIMULATIONCONTROL: 1
SIZING:PARAMETERS: 1
SIZING:ZONE: 4
SIZINGPERIOD:DESIGNDAY: 2
TIMESTEP: 1
VERSION: 1
ZONE: 4
ZONEHVAC:EQUIPMENTCONNECTIONS: 4
ZONEHVAC:EQUIPMENTLIST: 4
ZONEHVAC:UNITHEATER: 4
Total number of objects: 61
```

## PTHP

### Ruby call

```ruby
standard.model_add_hvac_system(osm,"PTHP", nil, nil, nil, osm.getThermalZones)
```
### Objects after the call

```
COIL:COOLING:DX:SINGLESPEED: 4
COIL:HEATING:DX:SINGLESPEED: 4
COIL:HEATING:ELECTRIC: 4
CURVE:BIQUADRATIC: 20
CURVE:CUBIC: 28
CURVE:EXPONENT: 4
CURVE:QUADRATIC: 40
FAN:ONOFF: 4
GLOBALGEOMETRYRULES: 1
LIFECYCLECOST:NONRECURRINGCOST: 1
LIFECYCLECOST:PARAMETERS: 1
LIFECYCLECOST:USEPRICEESCALATION: 5
NODELIST: 8
OUTDOORAIR:MIXER: 4
OUTDOORAIR:NODE: 1
OUTDOORAIR:NODELIST: 4
OUTPUT:SQLITE: 1
OUTPUT:TABLE:SUMMARYREPORTS: 1
OUTPUT:VARIABLEDICTIONARY: 1
OUTPUTCONTROL:TABLE:STYLE: 1
RUNPERIOD: 1
SCHEDULE:CONSTANT: 3
SCHEDULETYPELIMITS: 2
SIMULATIONCONTROL: 1
SIZING:PARAMETERS: 1
SIZING:ZONE: 4
SIZINGPERIOD:DESIGNDAY: 2
TIMESTEP: 1
VERSION: 1
ZONE: 4
ZONEHVAC:EQUIPMENTCONNECTIONS: 4
ZONEHVAC:EQUIPMENTLIST: 4
ZONEHVAC:PACKAGEDTERMINALHEATPUMP: 4
Total number of objects: 170
```

## PTAC, Electric

### Ruby call

```ruby
standard.model_add_hvac_system(osm,"PTAC", "Electricity", nil, nil, osm.getThermalZones)
```
### Objects after the call

```
BUILDING: 1
COIL:COOLING:DX:SINGLESPEED: 4
COIL:HEATING:ELECTRIC: 4
CURVE:BIQUADRATIC: 16
CURVE:CUBIC: 4
CURVE:EXPONENT: 4
CURVE:QUADRATIC: 24
FAN:ONOFF: 4
GLOBALGEOMETRYRULES: 1
LIFECYCLECOST:NONRECURRINGCOST: 1
LIFECYCLECOST:PARAMETERS: 1
LIFECYCLECOST:USEPRICEESCALATION: 5
NODELIST: 8
OUTDOORAIR:MIXER: 4
OUTDOORAIR:NODE: 1
OUTDOORAIR:NODELIST: 4
OUTPUT:SQLITE: 1
OUTPUT:TABLE:SUMMARYREPORTS: 1
OUTPUT:VARIABLEDICTIONARY: 1
OUTPUTCONTROL:TABLE:STYLE: 1
RUNPERIOD: 1
SCHEDULE:CONSTANT: 3
SCHEDULETYPELIMITS: 2
SIMULATIONCONTROL: 1
SIZING:PARAMETERS: 1
SIZING:ZONE: 4
SIZINGPERIOD:DESIGNDAY: 2
TIMESTEP: 1
VERSION: 1
ZONE: 4
ZONEHVAC:EQUIPMENTCONNECTIONS: 4
ZONEHVAC:EQUIPMENTLIST: 4
ZONEHVAC:PACKAGEDTERMINALAIRCONDITIONER: 4
Total number of objects: 122
```

## PTAC, Gas

### Ruby call

```ruby
standard.model_add_hvac_system(osm,"PTAC", "NaturalGas", nil, nil, osm.getThermalZones)
```
### Objects after the call

```
BOILER:HOTWATER: 1
BRANCH: 12
BRANCHLIST: 2
BUILDING: 1
COIL:COOLING:DX:SINGLESPEED: 4
COIL:HEATING:WATER: 4
CONNECTOR:MIXER: 2
CONNECTOR:SPLITTER: 2
CONNECTORLIST: 2
CURVE:BIQUADRATIC: 16
CURVE:CUBIC: 4
CURVE:EXPONENT: 4
CURVE:QUADRATIC: 24
FAN:ONOFF: 4
GLOBALGEOMETRYRULES: 1
LIFECYCLECOST:NONRECURRINGCOST: 1
LIFECYCLECOST:PARAMETERS: 1
LIFECYCLECOST:USEPRICEESCALATION: 5
NODELIST: 8
OUTDOORAIR:MIXER: 4
OUTDOORAIR:NODE: 1
OUTDOORAIR:NODELIST: 4
OUTPUT:SQLITE: 1
OUTPUT:TABLE:SUMMARYREPORTS: 1
OUTPUT:VARIABLEDICTIONARY: 1
OUTPUTCONTROL:TABLE:STYLE: 1
PIPE:ADIABATIC: 6
PLANTEQUIPMENTLIST: 1
PLANTEQUIPMENTOPERATION:HEATINGLOAD: 1
PLANTEQUIPMENTOPERATIONSCHEMES: 1
PLANTLOOP: 1
PUMP:VARIABLESPEED: 1
RUNPERIOD: 1
SCHEDULE:CONSTANT: 3
SCHEDULE:DAY:INTERVAL: 1
SCHEDULE:WEEK:DAILY: 1
SCHEDULE:YEAR: 1
SCHEDULETYPELIMITS: 3
SETPOINTMANAGER:SCHEDULED: 1
SIMULATIONCONTROL: 1
SIZING:PARAMETERS: 1
SIZING:PLANT: 1
SIZING:ZONE: 4
SIZINGPERIOD:DESIGNDAY: 2
TIMESTEP: 1
VERSION: 1
ZONE: 4
ZONEHVAC:EQUIPMENTCONNECTIONS: 4
ZONEHVAC:EQUIPMENTLIST: 4
ZONEHVAC:PACKAGEDTERMINALAIRCONDITIONER: 4
Total number of objects: 160
```
## Heating and Ventilation, Electric

### Ruby call

```ruby
standard.model_add_hvac_system(osm, "Unit Heaters", "Electricity", nil, nil, osm.getThermalZones)
```
### Objects after the call

```
BUILDING: 1
COIL:HEATING:ELECTRIC: 4
FAN:CONSTANTVOLUME: 4
GLOBALGEOMETRYRULES: 1
LIFECYCLECOST:NONRECURRINGCOST: 1
LIFECYCLECOST:PARAMETERS: 1
LIFECYCLECOST:USEPRICEESCALATION: 5
NODELIST: 8
OUTDOORAIR:NODE: 1
OUTPUT:SQLITE: 1
OUTPUT:TABLE:SUMMARYREPORTS: 1
OUTPUT:VARIABLEDICTIONARY: 1
OUTPUTCONTROL:TABLE:STYLE: 1
RUNPERIOD: 1
SCHEDULE:CONSTANT: 3
SCHEDULETYPELIMITS: 1
SIMULATIONCONTROL: 1
SIZING:PARAMETERS: 1
SIZING:ZONE: 4
SIZINGPERIOD:DESIGNDAY: 2
TIMESTEP: 1
VERSION: 1
ZONE: 4
ZONEHVAC:EQUIPMENTCONNECTIONS: 4
ZONEHVAC:EQUIPMENTLIST: 4
ZONEHVAC:UNITHEATER: 4
Total number of objects: 61
```

## PSZ-HP

### Ruby call

```ruby
standard.model_add_hvac_system(osm, "PSZ-HP", nil, nil, nil, osm.getThermalZones)
```
### Objects after the call

```
AIRLOOPHVAC: 4
AIRLOOPHVAC:CONTROLLERLIST: 4
AIRLOOPHVAC:OUTDOORAIRSYSTEM: 4
AIRLOOPHVAC:OUTDOORAIRSYSTEM:EQUIPMENTLIST: 4
AIRLOOPHVAC:RETURNPATH: 4
AIRLOOPHVAC:SUPPLYPATH: 4
AIRLOOPHVAC:UNITARYSYSTEM: 4
AIRLOOPHVAC:ZONEMIXER: 4
AIRLOOPHVAC:ZONESPLITTER: 4
AIRTERMINAL:SINGLEDUCT:CONSTANTVOLUME:NOREHEAT: 4
AVAILABILITYMANAGER:NIGHTCYCLE: 4
AVAILABILITYMANAGER:SCHEDULED: 4
AVAILABILITYMANAGERASSIGNMENTLIST: 8
BRANCH: 4
BRANCHLIST: 4
BUILDING: 1
COIL:COOLING:DX:SINGLESPEED: 4
COIL:HEATING:DX:SINGLESPEED: 4
COIL:HEATING:ELECTRIC: 4
CONTROLLER:MECHANICALVENTILATION: 4
CONTROLLER:OUTDOORAIR: 4
CURVE:BIQUADRATIC: 24
CURVE:CUBIC: 28
CURVE:EXPONENT: 4
CURVE:QUADRATIC: 40
FAN:ONOFF: 4
GLOBALGEOMETRYRULES: 1
LIFECYCLECOST:NONRECURRINGCOST: 1
LIFECYCLECOST:PARAMETERS: 1
LIFECYCLECOST:USEPRICEESCALATION: 5
NODELIST: 16
OUTDOORAIR:MIXER: 4
OUTDOORAIR:NODE: 1
OUTDOORAIR:NODELIST: 4
OUTPUT:SQLITE: 1
OUTPUT:TABLE:SUMMARYREPORTS: 1
OUTPUT:VARIABLEDICTIONARY: 1
OUTPUTCONTROL:TABLE:STYLE: 1
RUNPERIOD: 1
SCHEDULE:CONSTANT: 3
SCHEDULETYPELIMITS: 1
SETPOINTMANAGER:MIXEDAIR: 4
SETPOINTMANAGER:SINGLEZONE:REHEAT: 4
SIMULATIONCONTROL: 1
SIZING:PARAMETERS: 1
SIZING:SYSTEM: 4
SIZING:ZONE: 4
SIZINGPERIOD:DESIGNDAY: 2
TIMESTEP: 1
VERSION: 1
ZONE: 4
ZONEHVAC:AIRDISTRIBUTIONUNIT: 4
ZONEHVAC:EQUIPMENTCONNECTIONS: 4
ZONEHVAC:EQUIPMENTLIST: 4
Total number of objects: 265
```

## Packaged VAV, Gas Heating, Electric Reheat

### Ruby call

```ruby
uniquefloors.sort.each do |floor|
  floorzones = all_zones.select {|z| z.name.to_s.include? floor}
  puts "Adding PVAV_Gas for #{floor}"
  standard.model_add_hvac_system(osm,"PVAV Reheat", "NaturalGas", "Electricity", "Electricity", floorzones, hot_water_loop_type: "HighTemperature")
end
```
### Objects after the call

```
AIRLOOPHVAC: 1
AIRLOOPHVAC:CONTROLLERLIST: 2
AIRLOOPHVAC:OUTDOORAIRSYSTEM: 1
AIRLOOPHVAC:OUTDOORAIRSYSTEM:EQUIPMENTLIST: 1
AIRLOOPHVAC:RETURNPATH: 1
AIRLOOPHVAC:SUPPLYPATH: 1
AIRLOOPHVAC:ZONEMIXER: 1
AIRLOOPHVAC:ZONESPLITTER: 1
AIRTERMINAL:SINGLEDUCT:VAV:REHEAT: 4
AVAILABILITYMANAGER:NIGHTCYCLE: 1
AVAILABILITYMANAGER:SCHEDULED: 1
AVAILABILITYMANAGERASSIGNMENTLIST: 2
BOILER:HOTWATER: 1
BRANCH: 10
BRANCHLIST: 3
BUILDING: 1
COIL:COOLING:DX:TWOSPEED: 1
COIL:HEATING:ELECTRIC: 4
COIL:HEATING:WATER: 1
COILSYSTEM:COOLING:DX: 1
CONNECTOR:MIXER: 2
CONNECTOR:SPLITTER: 2
CONNECTORLIST: 2
CONTROLLER:MECHANICALVENTILATION: 1
CONTROLLER:OUTDOORAIR: 1
CONTROLLER:WATERCOIL: 1
CURVE:BIQUADRATIC: 4
CURVE:QUADRATIC: 3
DESIGNSPECIFICATION:ZONEAIRDISTRIBUTION: 4
FAN:VARIABLEVOLUME: 1
GLOBALGEOMETRYRULES: 1
LIFECYCLECOST:NONRECURRINGCOST: 1
LIFECYCLECOST:PARAMETERS: 1
LIFECYCLECOST:USEPRICEESCALATION: 5
NODELIST: 10
OUTDOORAIR:MIXER: 1
OUTDOORAIR:NODE: 1
OUTDOORAIR:NODELIST: 1
OUTPUT:SQLITE: 1
OUTPUT:TABLE:SUMMARYREPORTS: 1
OUTPUT:VARIABLEDICTIONARY: 1
OUTPUTCONTROL:TABLE:STYLE: 1
PIPE:ADIABATIC: 6
PLANTEQUIPMENTLIST: 1
PLANTEQUIPMENTOPERATION:HEATINGLOAD: 1
PLANTEQUIPMENTOPERATIONSCHEMES: 1
PLANTLOOP: 1
PUMP:VARIABLESPEED: 1
RUNPERIOD: 1
SCHEDULE:CONSTANT: 3
SCHEDULE:DAY:INTERVAL: 2
SCHEDULE:WEEK:DAILY: 2
SCHEDULE:YEAR: 2
SCHEDULETYPELIMITS: 2
SETPOINTMANAGER:MIXEDAIR: 3
SETPOINTMANAGER:SCHEDULED: 2
SIMULATIONCONTROL: 1
SIZING:PARAMETERS: 1
SIZING:PLANT: 1
SIZING:SYSTEM: 1
SIZING:ZONE: 4
SIZINGPERIOD:DESIGNDAY: 2
TIMESTEP: 1
VERSION: 1
ZONE: 4
ZONEHVAC:AIRDISTRIBUTIONUNIT: 4
ZONEHVAC:EQUIPMENTCONNECTIONS: 4
ZONEHVAC:EQUIPMENTLIST: 4
Total number of objects: 141
```

## WSHP (ignored)

### Ruby call

```ruby

```
### Objects after the call

```

```

## Four-Pipe Fan-Coil

### Ruby call

```ruby
standard.model_add_hvac_system(osm, "Fan Coil", "NaturalGas", nil, "Electricity", osm.getThermalZones, hot_water_loop_type: "HighTemperature", chilled_water_loop_cooling_type: "AirCooled")
```
### Objects after the call

```
BOILER:HOTWATER: 1
BRANCH: 24
BRANCHLIST: 4
BUILDING: 1
CHILLER:ELECTRIC:EIR: 1
COIL:COOLING:WATER: 4
COIL:HEATING:WATER: 4
CONNECTOR:MIXER: 4
CONNECTOR:SPLITTER: 4
CONNECTORLIST: 4
CURVE:BIQUADRATIC: 2
CURVE:CUBIC: 4
CURVE:EXPONENT: 4
CURVE:QUADRATIC: 1
FAN:ONOFF: 4
GLOBALGEOMETRYRULES: 1
LIFECYCLECOST:NONRECURRINGCOST: 1
LIFECYCLECOST:PARAMETERS: 1
LIFECYCLECOST:USEPRICEESCALATION: 5
NODELIST: 8
OUTDOORAIR:MIXER: 4
OUTDOORAIR:NODE: 1
OUTDOORAIR:NODELIST: 5
OUTPUT:SQLITE: 1
OUTPUT:TABLE:SUMMARYREPORTS: 1
OUTPUT:VARIABLEDICTIONARY: 1
OUTPUTCONTROL:TABLE:STYLE: 1
PIPE:ADIABATIC: 12
PLANTEQUIPMENTLIST: 2
PLANTEQUIPMENTOPERATION:COOLINGLOAD: 1
PLANTEQUIPMENTOPERATION:HEATINGLOAD: 1
PLANTEQUIPMENTOPERATIONSCHEMES: 2
PLANTLOOP: 2
PUMP:VARIABLESPEED: 2
RUNPERIOD: 1
SCHEDULE:CONSTANT: 3
SCHEDULE:DAY:INTERVAL: 2
SCHEDULE:WEEK:DAILY: 2
SCHEDULE:YEAR: 2
SCHEDULETYPELIMITS: 2
SETPOINTMANAGER:SCHEDULED: 2
SIMULATIONCONTROL: 1
SIZING:PARAMETERS: 1
SIZING:PLANT: 2
SIZING:ZONE: 4
SIZINGPERIOD:DESIGNDAY: 2
TIMESTEP: 1
VERSION: 1
ZONE: 4
ZONEHVAC:EQUIPMENTCONNECTIONS: 4
ZONEHVAC:EQUIPMENTLIST: 4
ZONEHVAC:FOURPIPEFANCOIL: 4
Total number of objects: 160
```

## VAV with PFP boxes

### Ruby call

```ruby
uniquefloors.sort.each do |floor|
  floorzones = all_zones.select {|z| z.name.to_s.include? floor}
  puts "Adding #{hvac_system_type} for #{floor}"
  standard.model_add_hvac_system(osm, "VAV PFP Boxes", nil, nil, nil, floorzones, hot_water_loop_type: nil, chilled_water_loop_cooling_type: "AirCooled")
end
```
### Objects after the call

```
AIRLOOPHVAC: 1
AIRLOOPHVAC:CONTROLLERLIST: 1
AIRLOOPHVAC:OUTDOORAIRSYSTEM: 1
AIRLOOPHVAC:OUTDOORAIRSYSTEM:EQUIPMENTLIST: 1
AIRLOOPHVAC:RETURNPATH: 1
AIRLOOPHVAC:SUPPLYPATH: 1
AIRLOOPHVAC:ZONEMIXER: 5
AIRLOOPHVAC:ZONESPLITTER: 1
AIRTERMINAL:SINGLEDUCT:PARALLELPIU:REHEAT: 4
AVAILABILITYMANAGER:NIGHTCYCLE: 1
AVAILABILITYMANAGER:SCHEDULED: 1
AVAILABILITYMANAGERASSIGNMENTLIST: 2
BRANCH: 1
BRANCHLIST: 1
BUILDING: 1
COIL:COOLING:DX:TWOSPEED: 1
COIL:HEATING:ELECTRIC: 5
COILSYSTEM:COOLING:DX: 1
CONTROLLER:MECHANICALVENTILATION: 1
CONTROLLER:OUTDOORAIR: 1
CURVE:BIQUADRATIC: 4
CURVE:QUADRATIC: 3
FAN:CONSTANTVOLUME: 4
FAN:VARIABLEVOLUME: 1
GLOBALGEOMETRYRULES: 1
LIFECYCLECOST:NONRECURRINGCOST: 1
LIFECYCLECOST:PARAMETERS: 1
LIFECYCLECOST:USEPRICEESCALATION: 5
NODELIST: 14
OUTDOORAIR:MIXER: 1
OUTDOORAIR:NODE: 1
OUTDOORAIR:NODELIST: 1
OUTPUT:SQLITE: 1
OUTPUT:TABLE:SUMMARYREPORTS: 1
OUTPUT:VARIABLEDICTIONARY: 1
OUTPUTCONTROL:TABLE:STYLE: 1
RUNPERIOD: 1
SCHEDULE:CONSTANT: 3
SCHEDULE:DAY:INTERVAL: 1
SCHEDULE:WEEK:DAILY: 1
SCHEDULE:YEAR: 1
SCHEDULETYPELIMITS: 2
SETPOINTMANAGER:MIXEDAIR: 3
SETPOINTMANAGER:SCHEDULED: 1
SIMULATIONCONTROL: 1
SIZING:PARAMETERS: 1
SIZING:SYSTEM: 1
SIZING:ZONE: 4
SIZINGPERIOD:DESIGNDAY: 2
TIMESTEP: 1
VERSION: 1
ZONE: 4
ZONEHVAC:AIRDISTRIBUTIONUNIT: 4
ZONEHVAC:EQUIPMENTCONNECTIONS: 4
ZONEHVAC:EQUIPMENTLIST: 4
Total number of objects: 113
```

## Packaged VAV with Reheat

### Ruby call

```ruby
uniquefloors.sort.each do |floor|
  floorzones = all_zones.select {|z| z.name.to_s.include? floor}
  puts "Adding #{hvac_system_type} for #{floor}"
  standard.model_add_hvac_system(osm,"PVAV Reheat", "NaturalGas", "NaturalGas", "Electricity", floorzones, hot_water_loop_type: "HighTemperature")
end
```
### Objects after the call

```
AIRLOOPHVAC: 1
AIRLOOPHVAC:CONTROLLERLIST: 2
AIRLOOPHVAC:OUTDOORAIRSYSTEM: 1
AIRLOOPHVAC:OUTDOORAIRSYSTEM:EQUIPMENTLIST: 1
AIRLOOPHVAC:RETURNPATH: 1
AIRLOOPHVAC:SUPPLYPATH: 1
AIRLOOPHVAC:ZONEMIXER: 1
AIRLOOPHVAC:ZONESPLITTER: 1
AIRTERMINAL:SINGLEDUCT:VAV:REHEAT: 4
AVAILABILITYMANAGER:NIGHTCYCLE: 1
AVAILABILITYMANAGER:SCHEDULED: 1
AVAILABILITYMANAGERASSIGNMENTLIST: 2
BOILER:HOTWATER: 1
BRANCH: 14
BRANCHLIST: 3
BUILDING: 1
COIL:COOLING:DX:TWOSPEED: 1
COIL:HEATING:WATER: 5
COILSYSTEM:COOLING:DX: 1
CONNECTOR:MIXER: 2
CONNECTOR:SPLITTER: 2
CONNECTORLIST: 2
CONTROLLER:MECHANICALVENTILATION: 1
CONTROLLER:OUTDOORAIR: 1
CONTROLLER:WATERCOIL: 1
CURVE:BIQUADRATIC: 4
CURVE:QUADRATIC: 3
DESIGNSPECIFICATION:ZONEAIRDISTRIBUTION: 4
FAN:VARIABLEVOLUME: 1
GLOBALGEOMETRYRULES: 1
LIFECYCLECOST:NONRECURRINGCOST: 1
LIFECYCLECOST:PARAMETERS: 1
LIFECYCLECOST:USEPRICEESCALATION: 5
NODELIST: 10
OUTDOORAIR:MIXER: 1
OUTDOORAIR:NODE: 1
OUTDOORAIR:NODELIST: 1
OUTPUT:SQLITE: 1
OUTPUT:TABLE:SUMMARYREPORTS: 1
OUTPUT:VARIABLEDICTIONARY: 1
OUTPUTCONTROL:TABLE:STYLE: 1
PIPE:ADIABATIC: 6
PLANTEQUIPMENTLIST: 1
PLANTEQUIPMENTOPERATION:HEATINGLOAD: 1
PLANTEQUIPMENTOPERATIONSCHEMES: 1
PLANTLOOP: 1
PUMP:VARIABLESPEED: 1
RUNPERIOD: 1
SCHEDULE:CONSTANT: 3
SCHEDULE:DAY:INTERVAL: 2
SCHEDULE:WEEK:DAILY: 2
SCHEDULE:YEAR: 2
SCHEDULETYPELIMITS: 2
SETPOINTMANAGER:MIXEDAIR: 3
SETPOINTMANAGER:SCHEDULED: 2
SIMULATIONCONTROL: 1
SIZING:PARAMETERS: 1
SIZING:PLANT: 1
SIZING:SYSTEM: 1
SIZING:ZONE: 4
SIZINGPERIOD:DESIGNDAY: 2
TIMESTEP: 1
VERSION: 1
ZONE: 4
ZONEHVAC:AIRDISTRIBUTIONUNIT: 4
ZONEHVAC:EQUIPMENTCONNECTIONS: 4
ZONEHVAC:EQUIPMENTLIST: 4
```
