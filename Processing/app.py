"""a basic connexion app called app.py"""
import os, datetime, connexion, json, yaml, logging, logging.config, logging.handlers, requests
from typing import Counter
from connexion import NoContent
from datetime import date
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS, cross_origin

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"
    
with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())
    
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    
logger = logging.getLogger('basicLogger')
logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

data_path = app_config['datastore']['filename']

# my functions
def get_stats():
    """ Gets order and scheduled order processsed statistics """
    logger.info("Request has started.")
    if os.path.exists(data_path):
        with open(data_path,"r")as f:
            data_list = json.load(f)
    else:
        logger.error("Statistics do not exist")

    print(data_list)

    logger.debug("The contents of the file are: %s" %(data_list))
    logger.info("The request has been completed")

    return data_list, 200
    # try:
    #     file=open(app_config["datastore"]["filename"], "r")
    #     file_content=file.read()
    #     file_content = json.loads(file_content)
    #     file.close()
    #     logger.debug(file_content)
    #     logger.info("Request has completed.")
    #     return file_content, 200
    # except:
    #     logger.error("Statistics do not exist.")
    #     return "Statistics do not exist.", 404


def populate_stats():
    """ Periodically update stats """

    logger.info("Start Periodic Processing")

    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%dT%H:%M:%SZ")

    if os.path.exists(data_path):
        with open(data_path,"r")as f:
            data_list = json.load(f)
    else:
        with open(data_path,"w") as f:
            data_list = {
                'num_order_readings':0,
                'num_sdorder_readings': 0,
                'max_order_reading':0,
                'max_sdorder_reading': 0,
                'last_updated': "2016-08-29T09:12:33Z"
            }
            f.write(json.dumps(data_list,indent=2))
        
        with open(data_path,"r")as f:
            data_list = json.load(f)
    
    current_num_order_readings = data_list['num_order_readings']
    current_num_sdorder_readings = data_list['num_sdorder_readings']
    current_max_order_reading = data_list['max_order_reading']
    current_max_sdorder_reading = data_list['max_sdorder_reading']
    preivous_time = data_list['last_updated']


    response1 = requests.get('http://kafkaservice.eastus2.cloudapp.azure.com/storage/food_delivery/order?start_timestamp=%s&end_timestamp=%s'%(preivous_time,formatted_time))
    if response1.status_code != 200:
        logger.debug("Error! didn't get 200 response code.")
    else:
        logger.info("successfully got the 200.")

    response2 = requests.get('http://kafkaservice.eastus2.cloudapp.azure.com/storage/food_delivery/scheduled_order?start_timestamp=%s&end_timestamp=%s'%(preivous_time,formatted_time))
    if response2.status_code != 200:
        logger.debug("Error! didn't get 200 response code.")
    else:
        logger.info("successfully got the 200.")
    

    total_num_or = (len(response1.json())+len(response2.json()))

    event_list = []
    event_list.append(len(response1.json()))
    event_list.append(len(response2.json()))
    total_amount_events = len(event_list)

    print(response1.json())
    print(response2.json())
    print(event_list)
    print(total_amount_events)
    
    data_list['num_order_readings'] = (len(response1.json())+current_num_order_readings)
    data_list['num_sdorder_readings'] = (len(response2.json())+current_num_sdorder_readings)
    data_list['max_order_reading'] = (total_num_or + current_max_order_reading)
    data_list['max_sdorder_reading'] =  (total_amount_events + current_max_sdorder_reading)
    data_list['last_updated'] = formatted_time 
    
    logger.info("Recieved %d events"% (total_amount_events))

    logger.debug("updated static values:")
    logger.debug("Updated the statistics values new values are: total reservation rentals = %d total same day rentals = %d " % (data_list['num_order_readings'],data_list['num_sdorder_readings']))
    
    with open(data_path,"w") as f:
        f.write(json.dumps(data_list,indent=2))

    logger.info("End Periodic Processing")


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,'interval',seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != 'test':
    CORS(app.app)
    app.app.config['CORS_HEADERS']='Content-Type'
app.add_api("openapi.yaml", base_path="/processing", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100)
