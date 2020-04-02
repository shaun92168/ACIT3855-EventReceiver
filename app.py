import connexion
import datetime
import yaml
import json
import logging.config
from pykafka import KafkaClient
from connexion import NoContent
from flask_cors import CORS

with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

STORE_SERVICE_SCAN_IN = "http://localhost:8090/scan_in"
STORE_SERVICE_BODY_INFO = "http://localhost:8090/body_info"
HEADERS = { "content-type": "application/json" }

logger = logging.getLogger('basicLogger')

def scan_in(ScanRecord):

    client = KafkaClient(hosts='{}:{}'.format(app_config['kafka']['server'], app_config['kafka']['port']))
    topic = client.topics[app_config['kafka']['topic']]
    producer = topic.get_sync_producer()
    msg = {"type": "ScanRecord", "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), "payload": ScanRecord}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info("adding new scan record")
    logger.debug(ScanRecord)

    return NoContent, 200

def update_body_info(BodyInfoUpdate):

    client = KafkaClient(hosts='{}:{}'.format(app_config['kafka']['server'], app_config['kafka']['port']))
    topic = client.topics[app_config['kafka']['topic']]
    producer = topic.get_sync_producer()
    msg = {"type": "BodyInfoUpdate", "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
           "payload": BodyInfoUpdate}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info("adding new body info record")
    logger.debug(BodyInfoUpdate)

    return NoContent, 200

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml")
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)
