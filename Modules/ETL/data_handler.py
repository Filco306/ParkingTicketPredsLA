import numpy as np
import pandas as pd

class DataHandler:
    def __init__(self):
        print("Fetching data")
        self.full_df = pd.read_pickle("Data/processed_data/df_all_cols_processed")
        self.density_vars = ["time_on_day_cx", "time_on_day_cy", "day_of_year_cx", "day_of_year_cy", "day_of_week_cx", "day_of_week_cy", "year_scaled", "lat_scaled", "lon_scaled", "is_holiday"]
        self.raw_vars = ["Year", "time_on_day","day_of_week", "day_of_year", "Latitude", "Longitude", "is_holiday"]
    def get_density_df(self):
        return self.full_df[self.density_vars]

    def get_raw_vars(self):
        return self.full_df[self.raw_vars]

    def slice(self, min_conditions = {}, max_conditions = {}, fixed_val_conditions = {}, df = None):
        if df is None:
            df = self.full_data

        for col in min_conditions:
            df = df.loc[df[col] >= min_conditions[col]]

        for col in max_conditions:
            df = df.loc[df[col] <= min_conditions[col]]

        for col in fixed_val_conditions:
            df = df.loc[df[col] == min_conditions[col]]

        return df
