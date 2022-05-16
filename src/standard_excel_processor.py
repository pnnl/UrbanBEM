#%%
import pandas as pd
from tqdm import tqdm
import json
import os

# os.chdir("/mnt/c/FirstClass/airflow/dags/urban-sim-flow/src")

#%%
data = pd.read_excel("../input/standardized_model_inputs_cbsa_04.22.2022.xlsx")

data = data.reindex(sorted(data.columns), axis=1)

#%%
std_cols = data.columns.values.tolist()

# %%
i = 0
for index, row in tqdm(data.iterrows(), total=data.shape[0]):
    if i == 1:
        case = {}
        for col in std_cols:
            case[col] = row[col]
        fname = f"../input/std_json_raw/{row['building_name']}.json"
        with open(fname, "w") as f:
            f.write(json.dumps(case, indent=4))
            print(f"{fname} saved")
        break
    else:
        i += 1
