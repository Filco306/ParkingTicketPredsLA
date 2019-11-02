import pandas as np
import numpy as np

class DataFetcher:
    def __init__(self, append_to_prev = True):
        self.append_to_prev = append_to_prev


    def get_new_data(self):
        print("Fetching the daily update of the data.")
