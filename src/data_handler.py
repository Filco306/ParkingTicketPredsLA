import logging
from src.db_connecting import get_postgis_conn
import re
import os

logging.basicConfig(level=os.environ.get("LOGGING_LEVEL", "INFO"))


class DataHandler:
    def __init__(self, conn=None):
        logging.info("Fetching data")
        logging.info("Going for it!")

        if conn is None:
            self.conn = get_postgis_conn()
        else:
            self.conn = conn

        self.density_vars = [
            "time_on_day_cx",
            "time_on_day_cy",
            "day_of_year_cx",
            "day_of_year_cy",
            "day_of_week_cx",
            "day_of_week_cy",
            "year_scaled",
            "lat_scaled",
            "lon_scaled",
            "is_holiday",
        ]
        self.raw_vars = [
            "Year",
            "time_on_day",
            "day_of_week",
            "day_of_year",
            "Latitude",
            "Longitude",
            "is_holiday",
        ]

    def rename_column(self, x):
        return re.sub(r"\W+", "", x).lower()

    def preprocess_and_ingest_into_postgres(self, cursor, df):
        pass

    def get_density_df(self):
        return self.full_df[self.density_vars]

    def get_raw_vars(self):
        return self.full_df[self.raw_vars]

    def slice(
        self, min_conditions={}, max_conditions={}, fixed_val_conditions={}, df=None
    ):
        if df is None:
            df = self.full_data

        for col in min_conditions:
            df = df.loc[df[col] >= min_conditions[col]]

        for col in max_conditions:
            df = df.loc[df[col] <= min_conditions[col]]

        for col in fixed_val_conditions:
            df = df.loc[df[col] == min_conditions[col]]

        return df
