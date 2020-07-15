#%%
import pandas as pd
from tqdm import tqdm
import json
import os

#os.chdir("/mnt/c/FirstClass/airflow/dags/urban-sim-flow/src")

#%%
data = pd.read_excel("../input/cbecs-standardized-200604.xlsx")

#%%
std_cols = data.columns.values.tolist()

# %%
i = 0
for index, row in tqdm(data.iterrows(), total=data.shape[0]):
    case = {}
    for col in std_cols:
        case[col] = row[col]
    fname = f"../input/std_json_raw/{row['building_name']}.json"
    with open(fname, "w") as f:
        f.write(json.dumps(case, indent=4))
        print(f"{fname} saved")
    # if i > 3:
    #     break  # TODO: delete this after dev
    i += 1