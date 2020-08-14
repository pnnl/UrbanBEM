import pandas as pd

#EnergyPlus output report class
class EPlusReport(dict):
	
	#Constructor accepting an unformatted dataframe version of the report
	def __init__(self, df):
		
		#Propogate table names downwards
		df[0] = df[0].fillna(method = 'ffill')
		
		#Map table names to reformatted dataframes
		for name in df.groupby(0).groups:
			
			# Extract and clean up dataframe
			self[name] = df.groupby(0).get_group(name)
			self[name] = self[name].drop(columns = 0)
			self[name] = self[name].dropna(axis = 'index', how = 'all')
			self[name] = self[name].dropna(axis = 'columns', how = 'all')
			
			# Delete if there is no table associated with the name - the CSV includes some entries in the first column which are not table names
			if self[name].empty:
				del self[name]
			
			# Otherwise, set the column label as the first row and set the index as the first column
			else:
				self[name] = self[name].rename(columns = self[name].iloc[0]).iloc[1:]
				self[name] = self[name].set_index(self[name].iloc[:, 0]).iloc[:, 1:]

#EnergyPlus output reports class
class EPlusOutputReports(dict):

	#Static number of columns, used to read gzipped files
	cols = 1
	
	#Constructor accepting the tables output filepath
	def __init__(self, path):
		
		#Read the csv to a dataframe
		while True:
			df = pd.read_csv(path, names = range(EPlusOutputReports.cols), dtype = 'object')
			if df[df.columns[-1]].isnull().all():
				break
			EPlusOutputReports.cols = EPlusOutputReports.cols + 1
			
		#Get report metadata
		self.programVersion = df[df[0].str.strip() == 'Program Version:'].iloc[0, 1]
		self.delimeter = df[df[0].str.strip() == 'Tabular Output Report in Format:'].iloc[0, 1]
		self.building = df[df[0].str.strip() == 'Building:'].iloc[0, 1]
		self.environment = df[df[0].str.strip() == 'Environment:'].iloc[0, 1]
		
		#Map report names to their respective EPlusReport objects
		reportDelimeterIndices = df[df[0] == '-' * 100].index.tolist()
		while len(reportDelimeterIndices) > 1:
			report = df.loc[reportDelimeterIndices.pop(0): reportDelimeterIndices[0]].copy()
			self[report.iloc[1, 1], report.iloc[2, 1]] = EPlusReport(report.iloc[3:-1].copy())
	