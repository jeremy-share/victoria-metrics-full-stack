import flask
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask_apscheduler import APScheduler
from flask_socketio import SocketIO, emit
from os import getenv
import secrets
import logging
import eventlet

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from dotenv import load_dotenv
from os.path import realpath, dirname
from dataclasses import dataclass
from typing import Dict
import socket
from datetime import datetime
from time import sleep

# https://stackoverflow.com/questions/71474916/is-it-possible-to-call-socketio-emit-from-a-job-scheduled-via-apscheduler-backg
eventlet.monkey_patch(thread=True, time=True)

logger = logging.getLogger(__name__)
root_dir = realpath(dirname(realpath(__file__)) + "/..")
load_dotenv(dotenv_path=f"{root_dir}/.env")
logging.basicConfig(level=getenv("LOGLEVEL", "INFO").upper())


class Config:
    SCHEDULER_API_ENABLED = False


@dataclass
class ClientDetails:
    sid: str  # More info can be added here


app = Flask(__name__)
app.config.from_object(Config())
sio = SocketIO(app, cors_allowed_origins="*")

hostname = socket.gethostname()
scheduler = BackgroundScheduler()
flask_scheduler = APScheduler(scheduler)
flask_scheduler.init_app(app)
logger.info("")

clients_by_sid: Dict[str, ClientDetails] = {}

run_port = getenv("RUN_PORT", 8080)
run_host = getenv("RUN_HOST", "0.0.0.0")
metrics_endpoint = getenv("METRICS_ENDPOINT")
metrics_token = getenv("METRICS_TOKEN")
metrics_org = "demo"
metrics_bucket = "backend-service"
metrics_prefix = "backend_service"

influxdb_client = InfluxDBClient(url=metrics_endpoint, token=metrics_token)
logger.info(f"Metrics url='{metrics_endpoint}' token='{metrics_token}'")
influxdb_client.default_tags = {}

write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)

detection_totals = {}


def get_ms_time():
    return datetime.now().microsecond


def time_decorator_factory(metric_name: str, tags=None):
    if tags is None:
        tags = {}

    def decorator(function):
        def wrapper(*args, **kwargs):
            start = get_ms_time()
            result = function(*args, **kwargs)
            end = get_ms_time()
            point = Point(metrics_prefix + "_" + metric_name)
            for key, value in tags.items():
                point.tag(key, value)
            total = end - start
            point.field("microsecond_time", total)
            write_api.write(metrics_bucket, metrics_org, point)
            return result
        return wrapper
    return decorator


def msg_all_clients(message: str, data=None):
    for client in list(clients_by_sid.keys()):
        try:
            sio.emit(message, data, to=client)
        except Exception:
            # Catch any single client send exceptions and report
            logger.exception("")


@sio.event
def connect():
    sid = flask.request.sid
    logger.info("SIO client connected '%s'", sid)
    clients_by_sid[sid] = ClientDetails(sid=sid)
    write_api.write(metrics_bucket, metrics_org, Point(metrics_prefix).field("client_connections", get_ms_time()))


@sio.event
def ping():
    logger.info("SIO received 'ping' from client")

    # Sleep for a random amount of time to simulate a network delay
    sleep_for_pre = secrets.choice(list(range(1, 5)))
    logger.info("ping - Sleeping for pre '%s'", sleep_for_pre)
    sleep(sleep_for_pre)

    # A timer is probably better than doing this
    write_api.write(metrics_bucket, metrics_org, Point(metrics_prefix).field("sio_pings", 1))

    # Sleep for a random amount of time to simulate a network delay
    sleep_for_post = secrets.choice(list(range(1, 5)))
    logger.info("ping - Sleeping for post '%s'", sleep_for_post)
    sleep(sleep_for_post)

    emit("pong", {})


@sio.event
def disconnect():
    sid = flask.request.sid
    logger.info("SIO client disconnected '%s'", sid)
    del clients_by_sid[sid]
    write_api.write(metrics_bucket, metrics_org, Point(metrics_prefix).field("client_disconnections", get_ms_time()))


@time_decorator_factory("detect")
def detect():
    detection_options = [0] + [0] + list(range(0, 8))

    # ===Random numbers like an AI detection===
    # fmt: off
    detections = {
        "car": secrets.choice(detection_options),
        "person": secrets.choice(detection_options),
        "cat": secrets.choice(detection_options),
        "dog": secrets.choice(detection_options)
    }
    # fmt: on
    points = set()
    for detection_code, detections_count in detections.items():
        points.add(
            Point(metrics_prefix + "_detections")
            .tag("code", detection_code)
            .tag("type", "reading")
            .field("type", detections_count)
        )
    write_api.write(metrics_bucket, metrics_org, points)

    return detections


def append_totals(detections: Dict[str, int]):
    points = set()
    for detection_code, detections_count in detections.items():
        new_total = detection_totals.get(detection_code, 0) + detections_count
        detection_totals[detection_code] = new_total
        points.add(
            Point(metrics_prefix + "_detections")
            .tag("type", detection_code)
            .tag("type", "total")
            .field("type", new_total)
        )
    write_api.write(metrics_bucket, metrics_org, points)


def send_detections():
    logger.info("")

    # Sleep for a random amount of time to simulate random events timing
    # Note: The scheduler is set to only run one concurrent version of this function
    sleep_for = secrets.choice(list(range(0, 3)))
    logger.info("ping - Sleeping for post '%s'", sleep_for)
    sleep(sleep_for)

    detections = detect()
    append_totals(detections)

    logger.info("Sending detections:")
    logger.info(detections)
    logger.info("Sending totals:")
    logger.info(detection_totals)
    msg_all_clients("detection", {'detections': detections, 'detection-totals': detection_totals})

    sent_point = Point(metrics_prefix + "") \
        .field("detections_sent", get_ms_time()) \
        .field("detections_count", sum(detections.values()))
    write_api.write(metrics_bucket, metrics_org, sent_point)


scheduler.add_job(send_detections, 'interval', seconds=1, max_instances=1)
flask_scheduler.start()

if __name__ == '__main__':
    sio.run(app, host=run_host, port=run_port)
