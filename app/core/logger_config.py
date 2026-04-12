import os
import logging
import pythonjsonlogger.jsonlogger as jsonlogger
from logstash_async.handler import AsynchronousLogstashHandler



logger = logging.getLogger("fastapi_elk")
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

logstash_handler = AsynchronousLogstashHandler(
    host=os.getenv("LOGSTASH_HOST", "logstash"),
    port=12201,
    database_path=None
    )

logger.addHandler(logstash_handler)