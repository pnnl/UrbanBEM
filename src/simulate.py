import sys
import os
import json
import subprocess
from traceback import print_exc

# Read casename from command line input
casename = sys.argv.pop()

#Standard output and standard error will be redirected to these files so they aren't printed on top of messages from other cases running in parallel
outFile = open(f'../ep_output/stdout/{casename}_out.txt', 'w')
errFile = open(f'../ep_output/stderr/{casename}_err.txt', 'w')

# Get weather filepath
with open(f'../input/std_json_raw/{casename}.json') as file:
      epw = json.load(file)['epw_file']

try:

	# Run the simulation
	completedSim = subprocess.run(['/qfs/projects/BECP/bin/runeplus',
	                               '-v', '9.5.0',
	                               '-x', 'eso,mtd,mtr,mdd,bnd,svg,zsz,ssz',
	                               '-w', '../resources/weather',
	                               '-o', str(casename),
	                               '-p', '../ep_output/output',
	                               f'../ep_input/input/{casename}.idf', epw],
	                               stdout = outFile,
	                               stderr = errFile)

except:

	print_exc(file = errFile)

outFile.close()
errFile.close()
