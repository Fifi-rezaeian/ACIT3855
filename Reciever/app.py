"""a basic connexion app called app.py"""
import connexion
from connexion import NoContent
import json
import os
import requests
import yaml
import logging
import logging.config
import logging.handlers
import datetime
from pykafka import KafkaClient, client
from yaml import events
import time


MAX_EVENT = 12
EVENT_FILE = "events.json"

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

# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)
logger.info("starting receiver for event messages")

#current_retries = 0
#while current_retries < app_config["maximum_number_of_retries"]:
    #logger.info("trying to connenct to kafka current retries = %d", (current_retries))
    #try:
        #client = KafkaClient(hosts=f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}')
        #topic = client.topics[str.encode(app_config["events"]["topic"])]
        #producer = topic.get_sync_producer()
        #currrent_retries = app_config["maximum_number_of_retries"]
    #except:
        #logger.error("connection failed to connenct to kafka")
        #time.sleep(app_config["sleep_time"])
        #current_retries += 1

# My Functions

def report_order_details(body):
    """ Receives order_details event """
    
    # POST request
    # headers = {"content-type": "application/json"}
    # response = requests.post(app_config["eventstore1"]["url"], json=body, headers=headers)
    # if response.status_code == 400: 
    #     # JSON response –has a built-in JSON decoder
    #     print(response.json())

    logger.info("Received event order request with a unique id of customer_id")
    

    client = KafkaClient(hosts=f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}')
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    producer = topic.get_sync_producer()

    msg = {"type": "Regular",
           "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
           "payload": body}

    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info("Returned event order response(Id: customer_id) with status 201")
    
    return NoContent, 201

    # if not os.path.exists(EVENT_FILE):
    #     open(EVENT_FILE, 'w+').close()

    # file=open(EVENT_FILE, "r")
    # #read the event_file to see if anything is there
    # file_content=file.read()
    # end_point = file_content.find(']')
    # file_content = file_content[:end_point + 1]
    # #convert json data to a python list
    
    # if len(file_content) < 1:
    #     #if the event_file is empty we need to create a list and add body into it
    #     file_content = []
    #     file_content.append(body)
    #     events = file_content
    # else:
    #     events = json.loads(file_content)
    #     events.append(body)

    #     # checks if the list lenghth is > 12, remove the oldest one 
    # if len(events) > MAX_EVENT:
    #     events.pop(0)
    # json_str = json.dumps(events, indent=2)
    # file=open(EVENT_FILE, "w")
    # file.write(json_str)
    # file.close()
    

def report_scheduled_order_details(body):
    """ Receives scheduled_order_details event """
    # POST request
    # headers = {"content-type": "application/json"}
    # response = requests.post(app_config["eventstore2"]["url"], json=body, headers=headers)
    # if response.status_code == 400: 
    #     # JSON response –has a built-in JSON decoder
    #     print(response.json())

    logger.info("Received event scheduled_order request with a unique id of customer_id")
    

    client = KafkaClient(hosts=f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}')
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    producer = topic.get_sync_producer()

    msg = {"type": "Scheduled",
           "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
           "payload": body}

    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info("Returned event scheduled_order response(Id: customer_id) with status 201")
    
    return NoContent, 201

    # if not os.path.exists(EVENT_FILE):
    #     open(EVENT_FILE, 'w+').close()

    # file=open(EVENT_FILE, "r")
    # #read the event_file to see if anything is there
    # file_content=file.read()
    # end_point = file_content.find(']')
    # file_content = file_content[:end_point + 1]
    # #convert json data to a python list
    # if len(file_content) < 1:
    #     #if the event_file is empty we need to create a list and add body into it
    #     file_content = []
    #     file_content.append(body)
    #     events = file_content
    # else:
    #     events = json.loads(file_content)
    #     events.append(body)
    #     # checks if the list lenghth is > 12, remove the oldest one 
    
    # if len(events) > MAX_EVENT:
    #     events.pop(0)

    # json_str = json.dumps(events, indent=2)
    # file=open(EVENT_FILE, "w")
    # file.write(json_str)
    # file.close()
    

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)
