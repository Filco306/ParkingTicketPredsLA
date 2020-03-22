from scipy import stats
from src.data_handler import DataHandler
import logging
import os

logging.basicConfig(level=os.environ.get("LOGGING_LEVEL", "INFO"))


class KernelModel:
    def __init__(self, dh=None, kernel_cols=None):
        if dh is None:
            self.dh = DataHandler()
        else:
            self.dh = dh

        if kernel_cols is None:
            self.kernel_cols = "all"
        else:
            self.kernel_cols = kernel_cols

        logging.info("Initializing")
        self.kde = None

    def train_model(self):

        if self.kernel_cols != "all":
            vals = self.dh.full_df[self.kernel_cols].values.T
        else:
            vals = self.dh.get_density_df().values.T

        self.kde = stats.gaussian_kde(vals)
        logging.info("Trained a kde")

    """
        Assumes a preprocessed df sent
        in and predicts, for each data point,
        a density prediction.

    """

    def get_densities(self, df=None):
        if self.kde is None:
            logging.info("No trained kde, training now. ")
            self.train_model()

        if df is None:
            df = self.dh.full_df

        if self.kernel_cols != "all":
            vals = df[self.kernel_cols].values.T
        else:
            vals = df.values.T
        return self.kde.evaluate(vals)
