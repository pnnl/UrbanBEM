#%%
import pandas as pd
from tqdm import tqdm
import json
import os

data = pd.read_excel("cbecs-standardized-200604.xlsx")

#%%
import numpy as np
np.sort(data['epw_file'].unique())

# %%
