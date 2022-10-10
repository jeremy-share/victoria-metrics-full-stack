import pprint

from flask import Flask, request, jsonify
from dotenv import load_dotenv
from os import getenv
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)


@app.route("/alert", methods=["post"])
def alert():
    logger.info("Alert received!")
    data = request.get_json()
    logger.info(pprint.pformat(data))
    logger.info("")
    return jsonify({})


if __name__ == "__main__":
    load_dotenv()
    is_debug = getenv('FLASK_DEBUG', "no").lower() in ["yes", "y", "t", "true"]
    logging.basicConfig(level=getenv("LOGLEVEL", "INFO"))
    app.run(debug=is_debug, host='0.0.0.0', port=5050)
