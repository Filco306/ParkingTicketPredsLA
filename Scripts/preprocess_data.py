from Modules.ETL.preprocessor import Preprocessor
import numpy as np
import pandas as pd


raw = pd.read_csv("Data/parking-citations.csv")
pp = Preprocessor(append_to_prev=False)

df = pp.full_preprocessing(raw)
print("Done")

df.to_pickle("Data/processed_data/df_all_cols_processed")
