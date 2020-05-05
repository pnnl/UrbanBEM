# urban-sim-flow

# Urban Simulation Framework

WIP

## Usage

(Airflow adoption on the new implementation is on hold.)

- Running the code requires the following environments:

  - Python 3.5+ (The code is tested with 3.7.5)
  - Apache-Airflow (The code is tested with Airflow 1.10.7 and its defautl DB of SQLite3)
  - Linux (I had some issues setting up Airflow on Windows. Running Airflow using Docker or WSL on Windows 10 are tested and good)

- Follow the [quick start guide](https://airflow.apache.org/docs/stable/start.html) to start the airflow service. Make sure to have environment variable `AIRFLOW_HOME` set up before running the the airflow db (`airflow scheduler`) and webserver(`airflow webserver -p 8080`). The database only needs to be initialized (`airflow initdb`) once, unless there are running errors. Before initializing the database, also make sure that `AIRFLOW_HOME` is set properly.
- If `AIRFLOW_HOME` is empty, then the airflow running folder is default to `~/airflow`.

## To-do list (short term)

- [ ] Redo HVAC processor with OpenStandard calls.
- [ ] confirm the appropriateness of the u values in CBECS and the construciton layer rules, most values lead to no insulation constructions
- [ ] Extract and compute ground temperature profile from the stat file
- [ ] Construct misc. objects and weather / location related objects
- [x] Adjust geometry processor to accomodate no core zone buildings (test with cbecs3)
- [x] Accomodate standard data schema
- [x] Add construction mapping in geometry processor
- [x] Specify schedule interface
- [x] Add multi-storey functionality

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
