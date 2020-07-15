import sys
import json
import subprocess

# Read casename from command line input
casename = sys.argv.pop()

# Get weather filepath
with open(f'../input/std_json_raw/{casename}.json') as file:
      epw = json.load(file)['epw_file']

# Run the simulation
completedSim = subprocess.run(['/projects/bigsim/bin/runeplus',
                               '-v', '9.0',
                               '-x', 'eso,mtd,mtr,mdd,bnd,svg,zsz,ssz',
                               '-w', '../resources/weather',
                               '-o', f'{casename}',
                               '-p', '../ep_output',
                               '-z',
                               f'../ep_input/input/{casename}.idf', epw])
