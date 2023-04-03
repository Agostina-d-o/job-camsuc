nexus_repository = dbutils.secrets.get(scope='ll2xxeuneakvcfgcommon',key= 'CfgNexusPipyRepository')
# COMMAND ----------
# MAGIC %pip install --index-url https://pypi.org/simple --extra-index-url $nexus_repository etl-camsuc==0.0.*

# COMMAND ----------

dbutils.widgets.text("Command", "create")  
dbutils.widgets.text("Database", "mg_mkt_master")
dbutils.widgets.text("Tables", "cam_journeytype, cam_successtype, cam_categorysegment, cam_segment, cam_campaign_successtype, cam_channel, cam_action")
dbutils.widgets.multiselect("NaProcess", "CrtTab", ["CrtTab"])
dbutils.widgets.text("CoCustomer", "ll2")
dbutils.widgets.text("Subdomain", "master")

# COMMAND ----------

command = dbutils.widgets.get('Command')
database = dbutils.widgets.get('Database')
tables = dbutils.widgets.get('Tables').split(',')
processes = dbutils.widgets.get('NaProcess').split(',')
CoCustomer = dbutils.widgets.get("CoCustomer")
subdomain = dbutils.widgets.get('Subdomain')

if (CoCustomer == ""):
    raise Exception("CoCustomer parameter is empty")

print('Command: ' + command)
print('Database: ' + database)
print(tables)
print('CoCustomer: ' + CoCustomer)
print('Subdomain: ' + subdomain)

# COMMAND ----------

import yaml
from llt.common.process.process import Process
from etl.camsuc.common.utils import set_config, get_adl_service  
from etl.camsuc.chain.process.table_management import get_loader         
import logging                                                   

# COMMAND ----------
set_config(processes, dbutils, CoCustomer)


# COMMAND ----------

formato = "%(asctime)s: %(message)s"
logging.basicConfig(format=formato, level=logging.INFO, datefmt="%H:%M:%S")   
logging.getLogger("py4j").setLevel(logging.ERROR)                            
logging.getLogger("azure.datalake.store.core").setLevel(logging.ERROR)        

# COMMAND ----------
adlclient = get_adl_service()
config_yaml_bytes = adlclient.read('/project/camsuc/config/processes/cam_table_management.yml')      
config = yaml.load(config_yaml_bytes, Loader=get_loader())

# COMMAND ----------
process = Process(**config['process_params'])
process.add_steps(config['steps'])
process(**{"command": command, "database": database, "table":tables, "subdomain":subdomain})