if __name__ == '__main__':
	
	from tqdm import tqdm
	from os import listdir
	from concurrent.futures import ProcessPoolExecutor
	from EPlusOutputReports import EPlusOutputReports
	import pandas as pd

	# Get all the valid case IDs
	validCases = [
		case for case in tqdm(range(1, 6721), desc = 'getting successful case numbers') 
		if any([f'cbecs{case}.' in filename for filename in listdir('../ep_output/output/')])
	]

	# Remove cases which encountered simulation errors
	validCases = [caseID for caseID in validCases if not open(f'../ep_output/stderr/cbecs{caseID}_err.txt', 'r').read()]

	# Get tables from EnergyPlus output
	with ProcessPoolExecutor() as executor:
		tables = dict(
			zip(
				validCases,
				tqdm(
					executor.map(
						EPlusOutputReports,
						[f'../ep_output/output/cbecs{caseID}.table.csv' for caseID in validCases]
					),
					total = len(validCases) - 1,
					desc = 'getting tables'
				)
			)
		)

	# Read the model check key excel file, which provides the location of relevant parameters in the tables
	modelCheckKey = pd.read_csv(
		'../resources/model_check-2020-07-27.csv', 
		index_col = 0
	)

	# Use the model check key to build the simulation summary dataframe
	simSummary = pd.DataFrame(
		{
			parameter: [
				tables[caseID][row['Report'], row['For']][row['Table']].loc[row['Row'], row['Column']] 
				for caseID in tables.keys()
			] 
			for parameter, row in tqdm(
				modelCheckKey.iterrows(),
				total = len(modelCheckKey.index),
				desc = 'building simulation summary'
			)
		}
	)

	# Set the simulation summary index as the respective case IDs
	simSummary.index = pd.Series(data = list(tables.keys()), name = 'Case ID')

	# Add a location column and fill it appropriately
	simSummary.insert(
		loc = 0, 
		column = 'Location', 
		value = [tables[caseID].environment for caseID in simSummary.index]
	)

	# Write the simulation summary to a csv file
	simSummary.to_csv('../output/simSummary.csv')