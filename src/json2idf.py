import os
from geomeppy import IDF
import json
from geometry import Geometry
from constructions import Constructions
from loads import Loads
from preprocessor import Preprocessor
from schedule_new import Schedule
from hvac import HVAC
from swh import SWH
from overhang import Overhang
from outputs import Outputs
import recipes
import sys
from traceback import print_exc

# Get the parameter, representing the CBECS case, passed to the command line
casename = 3306 #sys.argv.pop()

# Redirect the standard output and standard error to files so they aren't printed on top of messages from other cases running in parallel
sys.stdout = open(f"../ep_input/stdout/{casename}_out.txt", "w")
sys.stderr = open(f"../ep_input/stderr/{casename}_err.txt", "w")

# TODO: 0419
# 1. hvac and swh efficiency post processing
# 2. hvac template code version added to ruby call
# 3. htg/clg setpoint std inputs to module
# 4. number of door to door infiltration rate in preprocess
# 5. add guard to input lower case and keys check
# 6. allow unused keys in std input
# 7. ext lighting schedule to be always on and controlled by astronomical
# 8. swh flow schedule to be based on occ schedule = occ * 0.6 ( to be added to schedule preparation code)

try:

    # Set IDD
    IDF.setiddname("../resources/V9-5-0-Energy+.idd")

    #%% load minimal idf
    idf = IDF("../resources/idfs/Minimal.idf")
    case_path = f"../input/std_json_raw/{casename}.json"

    #%% convert units
    with open(case_path) as f:
        case = json.load(f)

    case = recipes.to_cbsa_hvac_type(case)

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
    scheduleadded_obj = Schedule(
        proc_case,
        constructionadded_obj.idf,
        randomizeHours=False,
        randomizeValues=False,
    )

    print(proc_case["zone_geometry"])

    # %% load processor
    loadadded_obj = Loads(proc_case, scheduleadded_obj.idf)

    # %% hvac processor
    hvacadded_obj = HVAC(proc_case, loadadded_obj.idf)

    # %% service water heating processor
    swhadded_obj = SWH(proc_case, hvacadded_obj.idf)

    # %% overhang processor
    overhangadded_obj = Overhang(proc_case, swhadded_obj.idf)

    # %% outputs processor
    outputsadded_obj = Outputs(proc_case, overhangadded_obj.idf)

    # Save idf
    outputsadded_obj.save_idf(f"../ep_input/input/{casename}.idf")

# If execution throws an exception, print message to error file but do not stop execution
except:

    print_exc()

sys.stdout.close()
sys.stderr.close()
