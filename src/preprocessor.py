import re
import pandas as pd
import numpy as np
from pyproj import Proj, transform
import holidays
from sklearn.preprocessing import MinMaxScaler


class Preprocessor:
    def __init__(self, append_to_prev=True):
        print("Initializing preprocessing")
        self.append_to_prev = append_to_prev

    def remove_nas(
        self,
        df,
        cols_to_remove_nas=[
            "Issue time",
            "Issue Date",
            "Latitude",
            "Longitude",
            "Location",
        ],
    ):
        """
            Drops na rows for the columns cols_to_remove_nas

        """
        for col in cols_to_remove_nas:
            df = df.loc[df[col].isna() == False]
        return df

    def get_holidays_data(self, df, time_col="Exact issuing time"):
        """
            Extracts, for each date,
            whether a date was a public holiday,
            and which day of the week it was.
            TODO: Transform this to weekly data rather,
            where both day of the week AND the time is used.
            The period, with circular transformation should 24*60*7
            and the
        """
        # https://pypi.org/project/holidays/
        us_holidays = holidays.CountryHoliday("US", prov=None, state="CA")
        df["is_holiday"] = df[time_col].apply(
            lambda x: 1 if us_holidays.get(x) is not None else 0
        )
        return df

    """
        Will remove coordinates that are not accurate
    """

    def convert_coordinates(
        self,
        df,
        remove_na_coords=True,
        longitude_box=[-120, -115],
        latitude_box=[32, 36],
    ):
        # Copied from another Kaggle user
        # Need to remember who
        # coords are in x/y
        # and we want lat/long, this is from the pyproj documentation
        pm = (
            "+proj=lcc +lat_1=34.03333333333333 +lat_2=35.46666666666667 +lat_0=33.5 +lon_0=-118 +x_0=2000000 "
            "+y_0=500000.0000000002 +ellps=GRS80 +datum=NAD83 +to_meter=0.3048006096012192 +no_defs"
        )
        df_bad_coords = df.loc[df["Latitude"] == 99999.0]
        df = df.loc[df["Latitude"] != 99999.0]

        # convert to lat/long
        x_in, y_in = df["Latitude"].values, df["Longitude"].values
        long, lat = transform(
            Proj(pm, preserve_units=True), Proj("+init=epsg:4326"), x_in, y_in
        )
        df.loc[:, "Latitude"] = lat
        df.loc[:, "Longitude"] = long

        # Ugly hardcoding: make all positive latitudes negative, make all negative longitudes positive
        df.loc[df["Latitude"] < 0, "Latitude"] = df.loc[
            df["Latitude"] < 0, "Latitude"
        ] * (-1)
        df.loc[df["Longitude"] > 0, "Longitude"] = df.loc[
            df["Longitude"] > 0, "Longitude"
        ] * (-1)

        df = df.loc[
            (df["Latitude"] >= latitude_box[0])
            & (df["Latitude"] <= latitude_box[1])
            & (df["Longitude"] >= longitude_box[0])
            & (df["Longitude"] <= longitude_box[1])
        ]

        return pd.concat([df, df_bad_coords], axis=0)

    def convert_date_to_hourly(self, df):
        df["Issue time"] = (
            df["Issue time"]
            .astype("int64")
            .astype("str")
            .str.pad(width=4, side="left", fillchar="0")
        )
        df["Issue time"] = (
            df["Issue time"].str.slice(stop=2)
            + ":"
            + df["Issue time"].str.slice(start=2)
            + ":00"
        )
        df["Exact issuing time"] = (
            df["Issue Date"].astype("str").str.slice(stop=11)
            + df["Issue time"].astype("str")
        ).astype("datetime64[ns]")
        # df = self.fix_time_vars(df)
        df.drop(["Issue Date", "Issue time"], axis=1, inplace=True)
        return df

    """
        Will impute, probabilistically,
        missing values for a specific column,
        based on other values.
        This is a very simple one,
        and a better approach would
        probably be to impute while regarding other columns as well.
    """

    def impute_probabilistically(self, df, col_to_impute, continuous=True):
        from scipy.stats import gaussian_kde

        density = gaussian_kde(df[col_to_impute].dropna())
        x = np.arange(0, df[col_to_impute].dropna().max())
        density = density.evaluate(x)
        # Normalize density to ensure sum of it is 1
        density = np.divide(density, np.sum(density))
        df.loc[df[col_to_impute].isna(), col_to_impute] = np.random.choice(
            x, p=density, size=df[col_to_impute].isna().sum()
        )
        return df

    def circular_transformation(self, df, col_name, period_length=24):
        """transforms one periodic pd.series into two pd.series

        input:

        df - pandas dataframe
        col_name - column with periodical values (hours, days, months, etc.)
        period_length - max units in a period (24 hours in a day, 60 seconds in
        one hour, 7 days in a week)

        no validation yet

        """
        s = df[col_name]
        s_x = s.apply(lambda x: np.sin(x / period_length * 2 * np.pi))
        s_y = s.apply(lambda x: np.cos(x / period_length * 2 * np.pi))
        kwargs = {col_name + "_cx": s_x, col_name + "_cy": s_y}
        return df.assign(**kwargs)

    def fix_time_vars(self, df, time_col="Exact issuing time"):
        df["time_on_day"] = df[time_col].dt.hour * 60 + df[time_col].dt.minute
        df = self.circular_transformation(df, "time_on_day", 60 * 24)
        df["day_of_year"] = df[time_col].dt.dayofyear
        df = self.circular_transformation(df, "day_of_year", 365)
        df["day_of_week"] = df[time_col].dt.weekday
        df = self.circular_transformation(df, "day_of_week", 7)
        df["Year"] = df["Exact issuing time"].dt.year

        df["month"] = df["Exact issuing time"].dt.month
        df = self.circular_transformation(df, "month", 12)

        df["day_of_month"] = df["Exact issuing time"].dt.day
        df = self.circular_transformation(df, "day_of_month", 31)
        sc = MinMaxScaler()
        df["year_scaled"] = sc.fit_transform(df["Year"].values.reshape(-1, 1))
        df["date issued"] = df["Exact issuing time"].dt.date
        return df

    def fix_spatial_vars(self, df, x_dim=100, y_dim=100):
        sc = MinMaxScaler()
        df["lat_scaled"] = sc.fit_transform(df["Latitude"].values.reshape(-1, 1))
        df["lon_scaled"] = sc.fit_transform(df["Longitude"].values.reshape(-1, 1))
        x = (np.ceil(df["lon_scaled"] * x_dim)).astype("int64")
        y = (np.ceil(df["lat_scaled"] * y_dim)).astype("int64")
        x.replace({0: 1}, inplace=True)
        y.replace({0: 1}, inplace=True)
        df["grid_x_sc"] = x / x_dim
        df["grid_y_sc"] = y / y_dim
        return df

    def generate_grid_points(self, x_dim, y_dim, time_start, time_end, time_step="1H"):
        all_time_sections = pd.date_range(start=time_start, end=time_end, freq="1H")
        x = np.linspace(0, 1, x_dim + 1)[1:]
        y = np.linspace(0, 1, y_dim + 1)[1:]
        n = pd.MultiIndex.from_product(
            [all_time_sections, x, y], names=["Time section", "grid_x", "grid_y"]
        )
        n = n.to_frame()
        n.columns = ["1", "2", "3"]
        n = n.reset_index().drop(["1", "2", "3"], axis=1)
        n = self.fix_time_vars(n, "Time section")
        n = self.get_holidays_data(n, "Time section")
        return n

    """
        Does a complete preprocessing
        of a raw dataframe
        incoming to do the density
    """

    def full_preprocessing(self, raw_df, verbose=True):
        if verbose:
            print("Removing the ones with NA-vals in important columns")
        df = self.remove_nas(raw_df)
        if verbose:
            print("Converting coordinates")
        df = self.convert_coordinates(df)
        df = df.merge(self.fix_locations(df), on="Ticket number")
        df.drop_duplicates(subset=["Ticket number"], inplace=True)
        imputed_coords = self.impute_coordinates(df)
        imputed_coords["is_imputed"] = True
        if verbose:
            print("Adding imputed coordinates from locations")
        df = df.merge(imputed_coords, how="left", on="Ticket number")
        df.loc[df["is_imputed"] == True, "Latitude"] = df.loc[
            df["is_imputed"] == True, "LAT"
        ]
        df.loc[df["is_imputed"] == True, "Longitude"] = df.loc[
            df["is_imputed"] == True, "LON"
        ]
        df = df.loc[df.Latitude != 99999.0]
        df.drop(
            [
                "HSE_DIR_CD_y",
                "HSE_NBR_y",
                "STR_SFX_CD_y",
                "STR_NM_y",
                "LAT",
                "LON",
                "is_imputed",
            ],
            axis=1,
            inplace=True,
        )
        print(list(df))
        df.columns = [
            "Ticket number",
            "Issue Date",
            "Issue time",
            "Meter Id",
            "Marked Time",
            "RP State Plate",
            "Plate Expiry Date",
            "VIN",
            "Make",
            "Body Style",
            "Color",
            "Location_x",
            "Route",
            "Agency",
            "Violation code",
            "Violation Description",
            "Fine amount",
            "Latitude",
            "Longitude",
            "Agency Description",
            "Color Description",
            "Body Style Description",
            "Location",
            "HSE_DIR_CD",
            "HSE_NBR",
            "STR_SFX_CD",
            "STR_NM",
        ]
        df = self.convert_date_to_hourly(df)
        df = df.loc[(df["Exact issuing time"].astype("int64") > 1.4 * 10 ** 18)]
        df = self.fill_nas(df)
        return df

    def get_street_name(self, x):
        to_check = [str(x["HSE_NBR"])]
        if x["HSE_DIR_CD"] is not None:
            to_check.append(x["HSE_DIR_CD"])

        if x["STR_SFX_CD"] is not None:
            to_check.append(x["STR_SFX_CD"])
        return " ".join(
            [
                s
                for s in x["Location"].split()
                if s not in to_check
                and str(x["HSE_NBR"]) not in s[: len(str(x["HSE_NBR"]))]
            ]
        )

    def impute_coordinates(self, df, df_has_loc_info=True):
        addresses_full = pd.read_csv("Data/addresses-in-the-city-of-los-angeles.csv")
        if df_has_loc_info is False:
            locations = self.fix_locations(df)
        else:
            locations = df[
                ["Ticket number", "HSE_DIR_CD", "HSE_NBR", "STR_SFX_CD", "STR_NM"]
            ]
        types = {
            "HSE_DIR_CD": "str",
            "HSE_NBR": "int64",
            "STR_SFX_CD": "str",
            "STR_NM": "str",
        }
        for col in types:
            addresses_full.loc[:, col] = addresses_full[col].astype(types[col])
            locations.loc[:, col] = locations[col].astype(types[col])
        addresses_full = addresses_full.applymap(
            lambda x: x.strip() if isinstance(x, str) else x
        )
        locations = locations.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        a = addresses_full[
            ["HSE_DIR_CD", "HSE_NBR", "STR_SFX_CD", "STR_NM", "LAT", "LON"]
        ].merge(locations, on=["HSE_DIR_CD", "HSE_NBR", "STR_SFX_CD", "STR_NM"])
        b = addresses_full[
            ["HSE_DIR_CD", "HSE_NBR", "STR_SFX_CD", "STR_NM", "LAT", "LON"]
        ].merge(locations, on=["HSE_NBR", "STR_SFX_CD", "STR_NM"])
        b = b.loc[b["HSE_DIR_CD_x"] != b["HSE_DIR_CD_y"]]
        b.rename({"HSE_DIR_CD_x": "HSE_DIR_CD"}, axis=1, inplace=True)
        b.drop(["HSE_DIR_CD_y"], axis=1, inplace=True)
        return pd.concat([a, b], axis=0).drop_duplicates(subset=["Ticket number"])

    def fix_locations(self, df):
        addresses_full = pd.read_csv("Data/addresses-in-the-city-of-los-angeles.csv")
        locations = pd.DataFrame(df[["Ticket number", "Location"]])
        # print(locations.head())
        locations["HSE_DIR_CD"] = locations["Location"].str.extract(
            r"(\bE\b|\bN\b|\bW\b|\bS\b)"
        )
        locations["HSE_NBR"] = locations["Location"].apply(
            lambda x: [
                s
                for s in x.split()
                if re.search(r"\d+", s) is not None
                and (any([y in s for y in ["ST", "RD", "ND", "TH"]]) == False)
            ]
        )
        locations["HSE_NBR"] = (
            locations["HSE_NBR"]
            .apply(lambda x: x[0] if len(x) > 0 else "")
            .str.extract(r"(\d+)")
        )
        locations["STR_SFX_CD"] = locations["Location"].str.extract(
            r"(\b"
            + "\\b|\\b".join(list(addresses_full.STR_SFX_CD.value_counts().index))
            + ")"
        )
        locations["HSE_NBR"].fillna(0, inplace=True)
        locations["STR_NM"] = locations.apply(lambda x: self.get_street_name(x), axis=1)

        return locations

    def extract_more_coordinates(self, df, df_has_loc_info=True):
        """
            Tries to extract as many
            coordinates as possible,
            and adds these new ones to the main data frame.
        """
        df = df.loc[df.Location.isna() == False]
        df_wo_coords = df.loc[df.Latitude == 99999.0]
        locations = self.impute_coordinates(df_wo_coords, df_has_loc_info)
        df_wo_coords = df_wo_coords.merge(
            locations[["Ticket number", "LAT", "LON"]], on="Ticket number", how="left"
        )
        df_wo_coords = df_wo_coords.drop(["Latitude", "Longitude"], axis=1).rename(
            {"LAT": "Latitude", "LON": "Longitude"}, axis=1
        )
        print(df_wo_coords.head())
        df_wo_coords.dropna(subset=["Latitude", "Longitude"], inplace=True)
        return pd.concat([df_wo_coords, df], axis=0).drop_duplicates(
            subset=["Ticket number"], keep="first"
        )

    def fill_nas(self, df):
        df = df.where(pd.notnull(df), None)
        return df
