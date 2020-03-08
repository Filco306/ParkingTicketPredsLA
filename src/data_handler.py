import pandas as pd
import os
from src.preprocessor import Preprocessor
import logging
import re
import psycopg2


class DataHandler:
    def __init__(self):
        logging.info("Fetching data")
        if os.path.exists("Data/processed_data/df_all_cols_processed") == False:
            self.full_df = self.preprocess_all()
        else:
            self.full_df = pd.read_pickle("Data/processed_data/df_all_cols_processed")
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

    def preprocess_all(self):
        # raw = pd.read_csv("Data/parking-citations.csv")
        pp = Preprocessor(append_to_prev=False)
        table = "PARKINGTICKET"
        chunksize = 10 ** 6

        conn = psycopg2.connect(
            "dbname='postgres' user='postgres' host='postgres' password='postgres'"
        )
        cur = conn.cursor()

        for chunk in pd.read_csv("Data/parking-citations.csv", chunksize=chunksize):
            df = pp.full_preprocessing(chunk)

            df.columns = [self.rename_column(x) for x in list(df)]
            df_dict = df.to_dict(orient="records")
            cur.executemany(
                """INSERT INTO {}({}) VALUES ({})""".format(
                    table,
                    ",".join(list(df.columns)),
                    "%(" + ")s,%(".join(list(df.columns)) + ")s",
                ),
                df_dict,
            )
        conn.close()

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
