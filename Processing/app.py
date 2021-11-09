"""a basic connexion app called app.py"""
import datetime
from typing import Counter
#from typing import OrderedDict
import connexion
from connexion import NoContent
import json
from datetime import date
import yaml
import logging
import logging.config
import logging.handlers
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS, cross_origin

with open("app_conf.yml", 'r') as f:
    app_config = yaml.safe_load(f.read())

with open("log_conf.yml", 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')


# my functions

def get_stats():
    """ Gets order and scheduled order processsed statistics """
    logger.info("Request has started.")
    try:
        file=open(app_config["datastore"]["filename"], "r")
        file_content=file.read()
        file_content = json.loads(file_content)
        file.close()
        logger.debug(file_content)
        logger.info("Request has completed.")
        return file_content, 200
    except:
        logger.error("Statistics do not exist.")
        return "Statistics do not exist.", 404


def populate_stats():
    """ Periodically update stats """

    logger.info("Start Periodic Processing")
    try: 
        file=open(app_config["datastore"]["filename"], "r")
        file_content=file.read()
        file_content = json.loads(file_content)
        file.close()
    except:
        with open(app_config["datastore"]["filename"], "w") as file:
            file.write(
                json.dumps({"num_order_readings":0,
                "max_order_reading":0, 
                "num_sdorder_readings":0, 
                "max_sdorder_reading":0,
                "last_updated": "2016-08-29T09:12:33Z"}))


    curr_time = date.today() 
    print("Today's date:", curr_time)

    headers = {"content-type": "application/json"}
    response1 = requests.get(app_config["eventstore1"]["url"], params={"timestamp": file_content["last_updated"]})
    if response1.status_code != 200:
        logger.debug("Error! didn't get 200 response code.")
    else:
        logger.info("successfully got the 200.")

    response2 = requests.get(app_config["eventstore2"]["url"], params={"timestamp":file_content["last_updated"]})
    if response2.status_code != 200:
        logger.debug("Error! didn't get 200 response code.")
    else:
        logger.info("successfully got the 200.")
    # print(response1.content)
    # print(response2.json())
    res_name_array_or = ""
    res_name_array_or = [el['resturant_name'] for el in json.loads(response1.content)]
    res_name_array_sor = ""
    res_name_array_sor = [el['resturant_name'] for el in json.loads(response2.content)]

    total_num_or = len(response1.json())+file_content['num_order_readings']

    total_num_max = file_content["max_order_reading"]
    logger.debug(res_name_array_or)
    if len(res_name_array_or) > 0:
        total_num_max = max(res_name_array_or)

    total_sor_num = len(response2.json())+file_content['num_sdorder_readings']
    
    total_sor_max = file_content["max_sdorder_reading"]
    logger.debug(res_name_array_sor)
    if len(res_name_array_sor) > 0:
        total_sor_max = max(res_name_array_sor)

    my_dict = {"num_order_readings":total_num_or, 
                "max_order_reading":total_num_max, 
                "num_sdorder_readings":total_sor_num, 
                "max_sdorder_reading":total_sor_max,
                "last_updated": datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%dT%H:%M:%SZ")}
    my_str = json.dumps(my_dict)
    
    file=open(app_config["datastore"]["filename"], "w")
    file.write(my_str)
    file.close()
    
    logger.debug("updated static values:")
    logger.debug(my_str)
    
    logger.info("End Periodic Processing")


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,'interval',seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, use_reloader=False)
