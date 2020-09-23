import os
from geomeppy import IDF
import json
from geometry import Geometry
from constructions import Constructions
from loads import Loads
from preprocessor import Preprocessor
from schedule_new import Schedule
from hvac import HVAC
from outputs import Outputs
import recipes
import sys
from traceback import print_exc

#Get the parameter, representing the CBECS case, passed to the command line
casename = sys.argv.pop()

#Redirect the standard output and standard error to files so they aren't printed on top of messages from other cases running in parallel
sys.stdout = open(f'../ep_input/stdout/{casename}_out.txt', 'w')
sys.stderr = open(f'../ep_input/stderr/{casename}_err.txt', 'w')

try:

	#Set IDD
	IDF.setiddname("../resources/Energy+V9_0_1.idd")

	#%% load minimal idf
	idf = IDF("../resources/idfs/Minimal.idf")
	case_path = f"../input/std_json_raw/{casename}.json"

	#%% convert units
	with open(case_path) as f:
	    case = json.load(f)

	if case['hvac_system_type'] in ['PSZ, Gas, SingleSpeedDX', 'PSZ, Electric, SingleSpeedDX', 'VAV, HotWater, ChilledWater']:

		case_conv, case_conv_clean = recipes.convert_dict_unit(case)

		with open(f"../input/std_json_conv/{casename}_conv.json", "w") as f:
		    f.write(json.dumps(case_conv, indent=4))
		with open(f"../input/std_json_conv_clean/{casename}_conv.json", "w") as f:
		    f.write(json.dumps(case_conv_clean, indent=4))

		#%% preprocessors
		proc_case = Preprocessor(case_conv_clean).case_proc
		with open(f"../input/processed_inputs/{casename}_processed.json", "w") as f:
		    f.write(json.dumps(proc_case, indent=4))

		#%% geometry processor
		geometryadded_obj = Geometry(proc_case, idf)

		#%% construction processor
		constructionadded_obj = Constructions(proc_case, geometryadded_obj.idf)
		
		# %% schedule processor
		scheduleadded_obj = Schedule(proc_case, constructionadded_obj.idf, randomize = True)

		# %% load processor
		loadadded_obj = Loads(proc_case, scheduleadded_obj.idf)

		# %% hvac processor
		hvacadded_obj = HVAC(proc_case, loadadded_obj.idf)

		# %% outputs processor
		outputsadded_obj = Outputs(proc_case, hvacadded_obj.idf)

		# Save idf
		outputsadded_obj.save_idf(f"../ep_input/input/{casename}.idf")

	else:

		print("HVAC system type not currenlty supported")

#If execution throws an exception, print message to error file but do not stop execution
except:

	print_exc()

sys.stdout.close()
sys.stderr.close()
