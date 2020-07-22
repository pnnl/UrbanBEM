import pandas as pd
import os.path

# Read the 2012 cbecs public use data csv
cbecs = pd.read_csv('../resources/2012_public_use_data_aug2016.csv', index_col = 'PUBID')

# Represents an aggregated subset of buildings derived from the CBECS dataset
# Used for electricity consumption analysis
class CBECS_BuildingStock:
	
	# Base constructor
	def __init__(self, weightMap, electricityConsumption, sqft, meters):
		
		# Get the weight dictionary, annual electricity consumption, square footage, and meters data
		self.weightMap = weightMap
		self.electricityConsumption = electricityConsumption
		self.sqft = sqft
		self.meters = meters
		
		# Calculate the simulated electricity consumption
		self.simConsumption = self.meters['Electricity:Facility [kWh](Hourly)'].sum()
		
		# Calculate the simulated electricity consumption as a percentage of the actual electricity consumption
		self.percentError = ((self.simConsumption/self.electricityConsumption) - 1) * 100

		# Calculate the energy intensity
		self.energyIntensity = self.electricityConsumption/self.sqft

		# Calculate the simulated energy intensity
		self.simIntensity = self.simConsumption/self.sqft
	
	# Alternate constructor which takes a .meter.csv EnergyPlus output file as an argument
	@classmethod
	def from_file(cls, meterFilepath):
		
		# Get the case ID, weight, annual electricity consumption, and square footage
		caseID = int(os.path.basename(meterFilepath).strip('cbecs').strip('.meter.csv'))
		weight = cbecs.loc[caseID].loc['FINALWT']
		weightMap = {caseID: weight}
		electricityConsumption = cbecs.loc[caseID].loc['ELCNS'] * weight
		sqft = cbecs.loc[caseID].loc['SQFT'] * weight
		
		# Read the simulated meters output
		meters = pd.read_csv(meterFilepath)
		
		# Convert the Date/Time entries into pandas Timestamp objects
		meters['Date/Time'] = pd.to_datetime(meters['Date/Time'].str.strip().str.replace('24:00:00', '00:00:00'), format = '%m/%d  %H:%M:%S').apply(pd.Timestamp.replace, year = 2012)
		
		# Set the Date/Time column as the index and sort the dataframe
		meters = meters.set_index('Date/Time').sort_index()
		meters.index = pd.DatetimeIndex(meters.index)
		
		# Convert the meters data from joules to kilowatt-hours
		meters = meters/(3.6 * 10 ** 6)
		meters = meters.rename(axis = 'columns', mapper = lambda x : x.replace('J', 'kWh'))
		
		# Multiply the meters data by its weight
		meters = meters * weight
		
		# Construct sample
		return cls(weightMap, electricityConsumption, sqft, meters)
	
	# Alternate constructor which takes the CBECS case number as an argument
	@classmethod
	def from_case(cls, caseID):
		
		# Construct sample
		return cls.from_file(f'../ep_output/output/cbecs{caseID}.meter.csv')
	
	# Adds two building stocks
	def __add__(self, right):
		
		# Combine the weightMap lists, add corresponding dataframe entries, and sum electricity consumption
		return CBECS_BuildingStock({**self.weightMap, **right.weightMap}, self.electricityConsumption + right.electricityConsumption, self.sqft + right.sqft, self.meters + right.meters)