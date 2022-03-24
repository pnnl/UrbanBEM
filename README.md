# urban-sim-flow

# Urban Simulation Framework

WIP

## `src` folder structure

| file name                      | Usage                                                                             |
| ------------------------------ | --------------------------------------------------------------------------------- |
| adaptors.py                    | adaptors for converting cbecs data to processor input                             |
| construction_meta_validator.py | validate construction meta json file (`../resources/construction_meta.json`)      |
| constructions.py               | construction processor                                                            |
| generate_hvac.rb               | ruby osstd hvac generation call file                                              |
| geometry.py                    | geometry processor                                                                |
| geometry_settings.json         | geometry processor config file                                                    |
| hvac.py                        | hvac processor                                                                    |
| hvac_settings.json             | hvac processor config file                                                        |
| loads.py                       | loads processor                                                                   |
| loads_settings.json            | loads processor config file                                                       |
| new_hvac.py                    | temperary hvac testing file for new hvac systems, not used in production workflow |
| preprocessor.py                | proprocessor used for organizing adaptors                                         |
| processed_loads_sample.json    | temporary file to show loads input format                                         |
| processed_schedule_sample.json | temporary file to show schedule input format                                      |
| rbcalls                        | temporary folder for ruby calls testing                                           |
| recipes.py                     | utility functions imported and used in other places                               |
| reference-2020-04-30.bib       | accidentally added ? lol ;D                                                       |
| schedule.py                    | schedule processor                                                                |
| schedule_database.json         | used by schedule processor, probably should be put in resources folder            |
| schedule_preparation.py        | used by schedule processor                                                        |
| schedule_settings.json         | schedule processor config file                                                    |
| standard_excel_processor.py    | generate raw input json files from excel spreadsheet                              |
| workflow.py                    | python cells to execute the whole workflow                                        |

## Parallel simulation workflow
- Insure you are using constance7a since normal constance doesn't have singularity.
- Currently, the source data comes from input/cbecs-standardized-200715.xlsx. Make any edits to input data here.
- cd into src/ subdirectory
- Run "sbatch run.sbatch"
- Track any output/error messages in the run.out and run.err text files

## Usage

(Airflow adoption on the new implementation is on hold.)

- Running the code requires the following environments:

  - Python 3.5+ (The code is tested with 3.7.5)
  - Apache-Airflow (The code is tested with Airflow 1.10.7 and its defautl DB of SQLite3)
  - Linux (I had some issues setting up Airflow on Windows. Running Airflow using Docker or WSL on Windows 10 are tested and good)

- Follow the [quick start guide](https://airflow.apache.org/docs/stable/start.html) to start the airflow service. Make sure to have environment variable `AIRFLOW_HOME` set up before running the the airflow db (`airflow scheduler`) and webserver(`airflow webserver -p 8080`). The database only needs to be initialized (`airflow initdb`) once, unless there are running errors. Before initializing the database, also make sure that `AIRFLOW_HOME` is set properly.
- If `AIRFLOW_HOME` is empty, then the airflow running folder is default to `~/airflow`.

<!-- ## To-do list (short term)

- [ ] Redo HVAC processor with OpenStandard calls.
- [ ] confirm the appropriateness of the u values in CBECS and the construciton layer rules, most values lead to no insulation constructions
- [ ] Extract and compute ground temperature profile from the stat file
- [ ] Construct misc. objects and weather / location related objects
- [x] Adjust geometry processor to accomodate no core zone buildings (test with cbecs3)
- [x] Accomodate standard data schema
- [x] Add construction mapping in geometry processor
- [x] Specify schedule interface
- [x] Add multi-storey functionality -->

## TO-DOs

- [ ] schedule change to non stochastic
- [ ] occupancy control: add occ based lighting control through schedule factor
- [ ] (code change) exterior fixtures: add one object (exterior lighting), with two inputs, schedule and design level.
- [ ] control electrical equipment schedule: similar to occupancy based lighting control
- [ ] (code change) improve electrical/gas equipment efficiency: add obe object for gas equipment
- [ ] (code change)shading overhang: add one object. one std input (overhang depth)
- [ ] (potential code change) vestibule / improve door: don't add door, but change infiltration rate and schedule. add std input: nodoor / door w/wo vestibule
- [ ] advanced control operation: change operation schedule
- [ ] HVAC setpoints
- [ ] (osstd code review before code change) economizer: check if economizer operation can be switched.
- [ ] (osstd code review before code change) DCV
- [ ] (osstd code review before code change) heat recovery: check ERV code in OSSTD
- [ ] (osstd code review before code change) SWH: check OSSTD. std input: swh efficiency, water temp setpoint.

## Updates

- 05/04/2020:
  - modify geometry processor to accomodate no core zone cases. Tested with CBECS 2 (w/ core) & 3 (w/o core).
- 05/03/2020:
  - Schedule preprocessor in place.
- 04/29/2020:
  - Construction processor and preprocessor in place.
- 04/25/2020:
  - Loads preprocessor in place.
- 04/20/2020:
  - Add standard input loading
  - modify unit conversion to include post-conversion units and addtitional conversions
- 04/21/2020:
  - Add multi-storey capacity
  - Add schedule generator interface.
  - Add loads generator interface.

## Dependencies

The following python pakcages need to be installed for using the framework

- eppy
- geomeppy
- esoreader
- apache-airflow
- notebook
- pandas

## Developer tools utilized

We use black to format python code of this repository

## Note

- Apache-airflow is used for workflow implementation and management. This modulize the framework and provides lots of features to run and manage the process. I also tried Metaflow and decided to go with Airflow because:

  1. Airflow has a feature-rich web-based UI, while Metaflow is purely CLI
  2. Metaflow has better documentation and community support, while Metaflow is just open-sourced
  3. Metaflow is AWS embeded, while Airflow are less oppinioned
  4. I tried to build AWS service for Metaflow and it is very non-trivial with bad documentation, while Airflow has AWS Batch operator already included (not tried yet)

- Sample I/O files are included in the repo at this moment for development purpose.
