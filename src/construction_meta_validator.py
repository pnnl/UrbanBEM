#%%
import json
import os

os.chdir("/mnt/c/FirstClass/airflow/dags/urban-sim-flow/src")

#%%
with open("../resources/construction_meta.json") as f:
    construction_meta = json.load(f)

#%%
mat_list = []
i = 0
for cons_surface, surface_types in construction_meta["construction"].items():
    for surface_cons, cons_layers in surface_types.items():
        mat_list.extend(cons_layers)
        i += 1

unique_mat_set = set(mat_list)

print(
    f"{i} typical constructions are identified, within which {len(unique_mat_set)} unique materials are identified\n"
)

#%%
defined_mat_list = set(construction_meta["material"].keys()).union(
    set(construction_meta["material_nomass"].keys())
)

unmatched_mat_set = unique_mat_set.symmetric_difference(defined_mat_list)

if len(unmatched_mat_set) > 0:
    print(f"There are unmatched materials: {unmatched_mat_set}")
else:
    print("Construction_meta ready to go!")
