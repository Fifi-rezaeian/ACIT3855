"""a basic connexion app called app.py"""
import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from order import Order
from scheduled_order import ScheduledOrder
import yaml
import logging
import logging.config
import logging.handlers
import datetime, json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
from sqlalchemy import and_

with open("app_conf.yml", 'r') as f:
    app_config = yaml.safe_load(f.read())

with open("log_conf.yml", 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

DB_ENGINE = create_engine(f'mysql+pymysql://{app_config["datastore"]["user"]}:{app_config["datastore"]["password"]}@{app_config["datastore"]["hostname"]}:{app_config["datastore"]["port"]}/{app_config["datastore"]["db"]}')
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

logger.info(f'connecting to DB. Hostname: {app_config["datastore"]["hostname"]}, Port: {app_config["datastore"]["port"]}')

# my functions
def report_order_details(body):
    """ Receives order_details event """

    session = DB_SESSION()

    order = Order(body['customer_id'],
                  body['resturant_name'],
                  body['delivery_loc'],
                  body['price'])

    session.add(order)

    session.commit()
    
    session.close()

    logger.debug("stored event order request with a unique id of customer_id")


def report_scheduled_order_details(body):
    """ Receives scheduled_order_details event """
    
    session = DB_SESSION()

    sdorder = ScheduledOrder(body['customer_id'],
                           body['resturant_name'],
                           body['delivery_loc'],
                           body['scheduled_time'])

    session.add(sdorder)
    
    session.commit()
    session.close()
    
    logger.debug("stored event scheduled order request with a unique id of customer_id")


def get_report_order_details(start_timestamp, end_timestamp):
    """ Gets new order details readings after the timestamp """

    session = DB_SESSION()
    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp,"%Y-%m-%dT%H:%M:%SZ")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")

    readings= session.query(Order).filter(
        and_(Order.date_created >= start_timestamp_datetime, Order.date_created < end_timestamp_datetime)
    )

    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())

    session.close()

    logger.info("Query for order details after %s returns %d results" % (start_timestamp, end_timestamp, len(results_list)))

    return results_list, 200


def get_report_scheduled_order_details(start_timestamp, end_timestamp):
    """ Gets new order details readings after the timestamp """

    session = DB_SESSION()
    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp,"%Y-%m-%dT%H:%M:%SZ")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")

    readings= session.query(ScheduledOrder).filter(
        and_(ScheduledOrder.date_created >= start_timestamp_datetime, ScheduledOrder.date_created < end_timestamp_datetime)
    )
    
    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())

    session.close()

    logger.info("Query for order details after %s returns %d results" % (start_timestamp, end_timestamp, len(results_list)))

    return results_list, 200


def process_messages():
    """ Process event messages """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    # Create a consume on a consumer group, that only reads new messages 
    # (uncommitted messages) when the service re-starts (i.e., it doesn't 
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                        reset_offset_on_start=False,
                                        auto_offset_reset=OffsetType.LATEST)
    # This is blocking -it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)

        payload = msg["payload"]

        if msg["type"] == "Regular": 
            # Store the event1 (i.e., the payload) to the DB
            report_order_details(payload)
        elif msg["type"] == "Scheduled": 
            # Store the event2 (i.e., the payload) to the DB
            report_scheduled_order_details(payload)
        # Commit the new message as being read
        consumer.commit_offsets()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090, debug=True)
