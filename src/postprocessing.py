import os
from CBECS_BuildingStock import CBECS_BuildingStock
from functools import reduce
import pandas as pd
import matplotlib.pyplot as plt

sampleStocks = [CBECS_BuildingStock.from_file(f'../ep_output/output/{filename}') for filename in os.listdir('../ep_output/output') if '.meter.csv' in filename]

stock = reduce(lambda a, b : a + b, sampleStocks)

stock.meters['Electricity:Facility [kWh](Hourly)'].plot(title = 'Aggregated Load Profile: CBECS Simulation')
ax = plt.gca()
ax.set_ylabel('Hourly Electricity Consumption [kWh]')
plt.savefig('../postprocessing/loadProfile', bbox_inches = 'tight')

results = pd.DataFrame(
	{'Weight': [list(case.weightMap.values())[0] for case in sampleStocks],
	 'Energy Intensity': [case.energyIntensity for case in sampleStocks],
	 'Simulated Energy Intensity': [case.simIntensity for case in sampleStocks],
	 'Percent Error': [case.percentError for case in sampleStocks],
	 'Annual Electricity Consumption': [case.electricityConsumption for case in sampleStocks]
	}, index = [list(case.weightMap.keys())[0] for case in sampleStocks]
)

results.to_csv('../postprocessing/results.csv', index_label = 'Case ID')


print(f'Annual Consumption Percent Error: {stock.percentError}%')
print(f'The average kWh was misrepresented by {sum([abs(case.percentError * case.electricityConsumption) for case in sampleStocks])/sum(case.electricityConsumption for case in sampleStocks)}%')
print(f'The average CBECS case was misrepresented by {sum([abs(error) for error in percentError])/len(sampleStocks)}%')