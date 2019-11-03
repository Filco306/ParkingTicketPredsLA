import numpy as np
from scipy import stats
from Modules.data_handler import DataHandler
class KernelModel:
    def __init__(self, dh = None, kernel_cols = None):
        if dh is None:
            self.dh = DataHandler()
        else:
            self.dh = dh

        if kernel_cols is None:
            self.kernel_cols = "all"
        else:
            self.kernel_cols = kernel_cols

        print("Initializing")
        self.kde = None


    def train_model(self):

        if self.kernel_cols != "all":
            vals = self.dh.full_df[self.kernel_cols].values.T
        else:
            vals = self.dh.get_density_df().values.T

        self.kde = stats.gaussian_kde(vals)
        print("Trained a kde")

    """
        Assumes a preprocessed df sent in and predicts, for each data point, a density prediction.

    """
    def get_densities(self, df = None):
        if self.kde is None:
            print("No trained kde, training now. ")
            self.train_model()

        if df is None:
            df = self.dh.full_df

        if self.kernel_cols != "all":
            vals = df[self.kernel_cols].values.T
        else:
            vals = df.values.T
        #vals = df.values.T
        return self.kde.evaluate(vals)
