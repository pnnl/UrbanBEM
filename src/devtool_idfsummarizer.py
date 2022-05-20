#%% load packages
from ast import If, In, Try
from itertools import count
from eppy import modeleditor
from eppy.modeleditor import IDF
import sys

try:
    idf_path = sys.argv[1]
except Exception as e:
    print(e)
    print("One argument to IDF file path is needed")
    exit()

IDF.setiddname("../resources/V9-5-0-Energy+.idd")
# %%
idf = IDF(idf_path)
# %%
full_objtype_list = list(idf.idfobjects)
# %%
obj_counter = {}
for obj_type in full_objtype_list:
    objs_per_type = idf.idfobjects[obj_type]
    if len(objs_per_type) > 0:
        obj_counter[obj_type] = len(objs_per_type)

obj_types_sorted = sorted(obj_counter)
counter = 0
for obj_type in obj_types_sorted:
    obj_count = obj_counter[obj_type]
    print(f"{obj_type}: {obj_count}")
    counter += obj_count
print(f"Total number of objects: {counter}")
