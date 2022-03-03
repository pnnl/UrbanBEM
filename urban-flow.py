# --------------------------------------------------------------------------------
# Written By: Jerry Lei
# Last Update: 01/06/2020
# This file should is a Apache-Airflow DAG with each step implemented.
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Load The Dependencies
# --------------------------------------------------------------------------------

import airflow
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime, timedelta
from pprint import pprint

import pandas as pd
import os, esoreader, math, subprocess
from geomeppy import IDF
import geomeppy.extractor

# --------------------------------------------------------------------------------
# data setting
# --------------------------------------------------------------------------------
cwd = "/mnt/c/FirstClass/airflow/dags/urban-sim-flow"
bcCSV = pd.read_csv(cwd + "/input/fake-bldg-characters.csv")
IDF.setiddname(cwd + "/resources/V9-5-0-Energy+.idd")

# --------------------------------------------------------------------------------
# task scripts
# --------------------------------------------------------------------------------


class ESO:
    def __init__(self, path):
        self.dd, self.data = esoreader.read(path)

    def read_var(self, variable, frequency="Hourly"):
        return [
            {"key": k, "series": self.data[self.dd.index[frequency, k, variable]]}
            for _f, k, _v in self.dd.find_variable(variable)
        ]

    def total_kwh(self, variable, frequency="Hourly"):
        j_per_kwh = 3_600_000
        results = self.read_var(variable, frequency)
        return sum(sum(s["series"]) for s in results) / j_per_kwh


def generateModel(dfRow, **kwargs):
    # using geomeepy to generate IDF

    # set starting point
    idf = IDF(cwd + "/resources/idfs/Minimal.idf")
    idf.epw = cwd + "/resources/weather/" + dfRow["weather"]

    sqft = float(dfRow["sqft"])
    numFls = int(dfRow["floors"])
    wwr = float(dfRow["wwr"])
    wallCons = dfRow["wall_construction_name"]

    # set geometry
    edge = int(math.sqrt(sqft / numFls))
    height = 3 * numFls
    blockName = str(numFls) + " floors block"

    idf.add_block(
        name=blockName,
        coordinates=[(edge, 0), (edge, edge), (0, edge), (0, 0)],
        height=height,
        num_stories=numFls,
    )
    idf.intersect_match()
    idf.set_default_constructions()

    # set windows
    idf.set_wwr(wwr=wwr, construction="Project External Window")

    # set wall construction
    wallSrcIdf = IDF(cwd + "/resources/idfs/CompositeWallConstructions.idf")
    geomeppy.extractor.copy_constructions(source_idf=wallSrcIdf, target_idf=idf)
    for wall in idf.getsurfaces("wall"):
        wall.Construction_Name = wallCons

    # add HVAC
    stat = idf.newidfobject(
        "HVACTEMPLATE:THERMOSTAT",
        Name="Zone Stat",
        Constant_Heating_Setpoint=20,
        Constant_Cooling_Setpoint=25,
    )
    for zone in idf.idfobjects["ZONE"]:
        idf.newidfobject(
            "HVACTEMPLATE:ZONE:IDEALLOADSAIRSYSTEM",
            Zone_Name=zone.Name,
            Template_Thermostat_Name=stat.Name,
        )

    # add outputs
    idf.newidfobject(
        "OUTPUT:VARIABLE",
        Variable_Name="Zone Ideal Loads Supply Air Total Heating Energy",
        Reporting_Frequency="Hourly",
    )
    idf.newidfobject(
        "OUTPUT:VARIABLE",
        Variable_Name="Zone Ideal Loads Supply Air Total Cooling Energy",
        Reporting_Frequency="Hourly",
    )

    # save
    idf.saveas(filename=cwd + "/output/" + dfRow["id"] + ".idf")

    return idf


def runModel(dfRow, genModelTaskId, **kwargs):

    # ti = kwargs["ti"]
    # idf = ti.xcom_pull(task_ids=genModelTaskId)

    # IDF.run(
    #     # idf=cwd + "/output/" + dfRow["id"] + ".idf",
    #     output_prefix=f"{dfRow['id']}_",
    #     output_directory=cwd + "/output/",
    #     expandobjects=True,
    #     ep_version="9-0-1",
    #     weather=cwd + "/resources/weather/" + dfRow["weather"],
    # )
    # # The above was the original try of using geomeppy to run the model, not smooth, and running ep in bash directly (as below) is more flexible and controllable.

    bashRun = [
        "/usr/local/EnergyPlus-9-0-1/energyplus",
        "--weather",
        cwd + "/resources/weather/" + dfRow["weather"],
        "--output-directory",
        cwd + "/output/",
        "--idd",
        cwd + "/resources/V9-5-0-Energy+.idd",
        "--expandobjects",
        "--output-prefix",
        dfRow["id"] + "_",
        cwd + "/output/" + dfRow["id"] + ".idf",
    ]

    compProc = subprocess.run(bashRun, capture_output=True)

    print("\nSTDOUT:")
    print(compProc.stdout)
    print("\nSTDERR")
    print(compProc.stderr)

    eso = ESO(f"{cwd}/output/{dfRow['id']}_out.eso")
    heat = eso.total_kwh("Zone Ideal Loads Supply Air Total Heating Energy")
    cool = eso.total_kwh("Zone Ideal Loads Supply Air Total Cooling Energy")
    simResult = [dfRow["id"], heat, cool, heat + cool]

    return simResult


def gatherResults(simTaskIds, **kwargs):
    ti = kwargs["ti"]
    resultList = ti.xcom_pull(task_ids=simTaskIds)
    print("\nGathered Results:")
    pprint(resultList)

    return resultList


# --------------------------------------------------------------------------------
# set default arguments
# --------------------------------------------------------------------------------

default_args = {
    "owner": "Jerry Lei",
    "depends_on_past": False,
    "start_date": airflow.utils.dates.days_ago(2),
    # 'start_date': datetime(2020, 1, 2),
    "email": ["leijerry888@gmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "provide_context": True,
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG("urban_workflow", default_args=default_args, schedule_interval=None)

start = DummyOperator(task_id="start", dag=dag)

join = DummyOperator(task_id="join", dag=dag)

simTaskIdList = []
for index, row in bcCSV.iterrows():

    # --------------------------------------------------------------------------------
    # generate model for each csv row
    # --------------------------------------------------------------------------------

    generate_model = PythonOperator(
        task_id="generate_model_" + row["id"],
        python_callable=generateModel,
        op_kwargs={"dfRow": row},
        dag=dag,
    )

    # --------------------------------------------------------------------------------
    # run model
    # --------------------------------------------------------------------------------

    run_model = PythonOperator(
        task_id="run_model_" + row["id"],
        python_callable=runModel,
        op_kwargs={
            "dfRow": row,
            "genModelTaskId": "generate_model_" + row["id"],
        },  # {"idfFile": idf, "weatherFile": weather},
        dag=dag,
    )

    simTaskIdList.append("run_model_" + row["id"])
    start >> generate_model >> run_model >> join

# --------------------------------------------------------------------------------
# gather results
# --------------------------------------------------------------------------------


gather_results = PythonOperator(
    task_id="gather_data",
    python_callable=gatherResults,
    op_kwargs={"simTaskIds": simTaskIdList},
    dag=dag,
)

join >> gather_results
