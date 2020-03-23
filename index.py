from run import app
import logging
import os

logging.basicConfig(level=os.environ.get("LOGGING_LEVEL", "INFO"))

if __name__ == "__main__":
    app.run("0.0.0.0", debug=False)
