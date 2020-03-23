from src.db_connecting import ingest_raw_parkingtickets, ingest_addresses
from src.preprocessor import batch_preprocessing
import logging
import os

logging.basicConfig(level=os.environ.get("LOGGING_LEVEL", "INFO"))
ingest_raw_parkingtickets()
ingest_addresses()
logging.info("Preprocessing the data!")
batch_preprocessing()
