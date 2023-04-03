nexus_repository = dbutils.secrets.get(scope='ll2xxeuneakvcfgcommon',key= 'CfgNexusPipyRepository')
# COMMAND ----------
# MAGIC %pip install --index-url https://pypi.org/simple --extra-index-url $nexus_repository etl-camsuc==0.0.*

# COMMAND ----------
import yaml
from llt.common.process.process import Process
from etl.camsuc.common.utils import set_config, get_adl_service
from etl.camsuc.chain.process.cam_controlgroup import get_loader as cg_loader
from datetime import datetime, timedelta

# COMMAND ----------
dbutils.widgets.text("NaProcess", "")
dbutils.widgets.text("DtProcessEnd", "")
dbutils.widgets.text("DtProcessStart", "")
dbutils.widgets.text("VlUmbral", "")
dbutils.widgets.text("CoCustomer", "")

DtProcessEnd = dbutils.widgets.get('DtProcessEnd')
DtProcessStart = dbutils.widgets.get('DtProcessStart')
umbral = dbutils.widgets.get('VlUmbral')
processes = dbutils.widgets.get('NaProcess')
CoCustomer = dbutils.widgets.get("CoCustomer")
date_format = "%Y-%m-%d"

# COMMAND ----------

if (CoCustomer == ""):
    raise Exception("CoCustomer parameter is empty")

if (umbral == ""):
    raise Exception("VlUmbral  parameter is empty")
umbral = int(umbral)
 
try:
    dt_process_end = datetime.strptime(DtProcessEnd, date_format)
    dt_process_start = datetime.strptime(DtProcessStart, date_format)
    
except ValueError:
    raise ValueError(" Error en los parámetros - Las fechas informadas deben tener formato YYYY-MM-DD")

if (dt_process_start > dt_process_end):
  raise Exception (" Error en las fechas  - La fechas de inicio es mayor que la fecha de fin")

DtProcessEnd = dt_process_end.strftime(date_format)
DtProcessStart = dt_process_start.strftime(date_format)

print('StartDtProcess: ' + DtProcessEnd)
print('EndDtProcess: ' + DtProcessStart)
print('processes: ' + processes )
print('VlUmbral: ' + str(umbral))
print('CoCustomer: ' + CoCustomer)

# COMMAND ----------

dates_to_process = []

while dt_process_start <= dt_process_end:
  dates_to_process.append(dt_process_start.strftime(date_format))
  dt_process_start = dt_process_start + timedelta(days= 1)

print("Dates to process ([start,end]): ", dates_to_process)

# COMMAND ----------

set_config(processes, dbutils, CoCustomer)

adlclient = get_adl_service()
config_cg= adlclient.read('/project/camsuc/config/processes/cam_controlgroup.yml')
config_cg = yaml.load(config_cg, Loader=cg_loader())

if 'RaSeCg' in processes:
  for date in dates_to_process:
    process_cg = Process(**config_cg['process_params'])
    process_cg.set_parameters(**{"DtProcess": date, "CoCustomer": CoCustomer, "VlUmbral": umbral})
    process_cg.set_planning_steps(config_cg['steps'])
    process_cg()