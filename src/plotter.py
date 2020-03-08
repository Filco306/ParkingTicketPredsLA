import math
from src.data_handler import DataHandler
from bokeh.models import Button
from bokeh.models.widgets import Slider, Select
from bokeh.models.widgets.inputs import DatePicker, MultiSelect
from datetime import date
import numpy as np
from bokeh.tile_providers import get_provider, Vendors
from bokeh.layouts import column, layout
from bokeh.models import BoxSelectTool, LassoSelectTool, ColumnDataSource
from bokeh.plotting import figure
from sklearn.cluster import KMeans
import logging


class Plotter:
    def __init__(self, dh=None):
        logging.info("Let's plot some stuff!")
        if dh is None:
            self.dh = DataHandler()
        else:
            self.dh = dh

    def plot_bar_chart(self, col="day_of_week"):
        logging.info("Plotting bar chart with " + col)
        c = self.dh.full_df[col]

        indices = c.value_counts().sort_index().index
        logging.info(c.value_counts().sort_index().values)
        p = figure(x_range=[str(x) for x in list(indices)], plot_height=250, title=col)
        p.vbar(x=indices + 0.5, top=c.value_counts().sort_index().values, width=0.9)

        p.xgrid.grid_line_color = None
        p.y_range.start = 0
        return p

    # Completely copied from https://towardsdatascience.com/exploring-and-visualizing-chicago-transit-data-using-pandas-and-bokeh-part-ii-intro-to-bokeh-5dca6c5ced10
    # And then remade
    def merc(self, lat, lon):
        # Coordinates = literal_eval(Coords)
        # lat = Coordinates[0]
        # lon = Coordinates[1]

        r_major = 6378137.000
        x = r_major * np.radians(lon)
        scale = x / lon
        y = (
            180.0
            / np.pi
            * np.log(np.tan(np.pi / 4.0 + lat * (np.pi / 180.0) / 2.0))
            * scale
        )
        return (x, y)

    """
        Generates a number of colors to use for the different clusters when clustering using k-means.

    """

    def generate_n_colors(self, n):
        import random

        number_of_colors = n

        color = [
            "#" + "".join([random.choice("0123456789ABCDEF") for j in range(6)])
            for i in range(number_of_colors)
        ]
        return color

    def create_bar_plot(self, col, df, top_x):

        indices = [str(x) for x in list(df[col].value_counts().index)][:top_x]
        heights = df[col].value_counts()
        bar_source = ColumnDataSource(
            data=dict(
                indices=indices,
                heights=heights.loc[heights.reset_index().index < top_x],
            )
        )
        TOOLTIPS = [(col, "@indices"), ("Frequency", "@heights")]
        bar_plot = figure(
            x_range=[str(x) for x in list(indices)][:top_x],
            plot_height=250,
            title=col,
            tooltips=TOOLTIPS,
        )
        bar_plot.vbar(x="indices", top="heights", width=0.9, source=bar_source)

        bar_plot.xgrid.grid_line_color = None
        bar_plot.y_range.start = 0
        bar_plot.xaxis.major_label_orientation = math.pi / 2
        return bar_source, bar_plot

    def test_hist(self, doc):

        default_bar_var = "STR_NM"
        min_date = date(2019, 9, 16)  # date.today() - timedelta(days = 1)
        max_date = date(2019, 9, 17)  # date.today()
        self.n_clusters = 4
        default_top = 10

        df = self.dh.full_df
        logging.info("Here we are now")

        logging.info("Training")
        self.km = KMeans(n_clusters=self.n_clusters)
        self.km.fit_transform(df[["Latitude", "Longitude"]])
        logging.info("Finished training")
        df = df.loc[(df["date issued"] >= min_date) & (df["date issued"] <= max_date)]

        # Now: create bar chart!

        bar_source, bar_plot = self.create_bar_plot(default_bar_var, df, default_top)
        self.bar_var_chosen = default_bar_var
        df = (
            df.groupby(["Location", "Latitude", "Longitude"])
            .count()
            .reset_index()[["Location", "Latitude", "Longitude", "Exact issuing time"]]
        )
        df = df.loc[df.index < 1000]
        self.colours = self.generate_n_colors(self.n_clusters)
        TOOLS = "pan,wheel_zoom,box_select,lasso_select,reset"

        lon, lat = self.merc(df["Latitude"], df["Longitude"])

        source = ColumnDataSource(
            data=dict(
                lon=df["Longitude"],
                lat=df["Latitude"],
                loc=df["Location"],
                amount_of_tickets=df["Exact issuing time"],
                colors_chosen=[
                    self.colours[x]
                    for x in self.km.predict(df[["Latitude", "Longitude"]])
                ],
                x=lon,
                y=lat,
                amt=3
                * np.log1p(df["Exact issuing time"])
                / np.min(np.log1p(df["Exact issuing time"])),
            )
        )
        TOOLTIPS = [
            ("Location", "@loc"),
            ("Latitude", "@lat"),
            ("Longitude", "@lon"),
            ("Amount of tickets", "@amount_of_tickets"),
        ]
        p = figure(
            tools=TOOLS,
            plot_width=600,
            plot_height=600,
            min_border=10,
            min_border_left=50,
            tooltips=TOOLTIPS,
            toolbar_location="above",
            x_axis_location=None,
            y_axis_location=None,
            title="Summary of parking tickets in LA",
            x_axis_type="mercator",
            y_axis_type="mercator",
        )
        p.add_tile(get_provider(Vendors.CARTODBPOSITRON))
        p.background_fill_color = "#fafafa"
        p.select(BoxSelectTool).select_every_mousemove = False
        p.select(LassoSelectTool).select_every_mousemove = False

        p.scatter(
            x="x", y="y", size="amt", source=source, color="colors_chosen", alpha=0.6
        )

        starting_date = DatePicker(
            title="Date Range: ",
            min_date=self.dh.full_df["date issued"].min(),
            max_date=self.dh.full_df["date issued"].max(),
            value=min_date,
        )
        ending_date = DatePicker(
            title="Date Range: ",
            min_date=self.dh.full_df["date issued"].min(),
            max_date=self.dh.full_df["date issued"].max(),
            value=max_date,
        )
        max_amount_of_points = Slider(
            title="Number of points in scatter: ",
            start=500,
            end=1000000,
            step=500,
            value=1000,
        )
        nClusters = Slider(
            title="Number of clusters (may take some time to retrain): ",
            start=2,
            end=15,
            step=1,
            value=4,
        )
        multi_select = MultiSelect(
            title="Which cars makes to include:",
            value=list(self.dh.full_df.Make.value_counts().index),
            options=list(self.dh.full_df.Make.value_counts().index),
        )

        select_bar_variable = Select(
            title="",
            value=default_bar_var,
            options=[
                ("Make", "Make"),
                ("Violation Description", "Violation Description"),
                ("Agency", "Agency"),
                ("STR_NM", "Street"),
            ],
        )
        show_top = Slider(
            title="Show top x in bar chart: ",
            start=5,
            end=200,
            step=5,
            value=default_top,
        )
        submit_button = Button(label="Update map")

        def select_data():
            logging.info("BEFORE MINDATE")
            mindate = starting_date.value
            maxdate = ending_date.value
            df = self.dh.full_df
            logging.info("HERE NOW ")
            logging.info(maxdate)
            logging.info(mindate)
            df = df.loc[
                (df["date issued"] >= mindate)
                & (df["date issued"] <= maxdate)
                & (df.Make.isin(multi_select.value))
            ]
            logging.info("Here, selecting data")
            logging.info("max amt of points is ")
            logging.info(max_amount_of_points.value)
            logging.info(type(max_amount_of_points.value))
            self.bar_var_chosen = select_bar_variable.value
            bar_source_new, _ = self.create_bar_plot(
                self.bar_var_chosen, df, show_top.value
            )
            indices = [
                str(x) for x in list(df[self.bar_var_chosen].value_counts().index)
            ]
            bar_plot.x_range.factors = [str(x) for x in list(indices)][: show_top.value]
            df = (
                df.groupby(["Location", "Latitude", "Longitude"])
                .count()
                .reset_index()
                .sort_values(by="Exact issuing time", ascending=False)
            )
            return (
                bar_source_new,
                df.loc[
                    df.index < max_amount_of_points.value,
                    ["Location", "Latitude", "Longitude", "Exact issuing time"],
                ],
            )

        def update():
            submit_button.label = "Updating..."
            logging.info("In update")
            # TODO: Only update if Make, min_date or max_date is changed
            bar_source_new, df = select_data()

            # TODO: Do not re-render each time

            bar_source.data = bar_source_new.data

            # Fix

            logging.info("DF should be changed?")
            logging.info(df)
            logging.info(df.shape)
            if nClusters.value != self.n_clusters:  # then retrain!
                logging.info("Retraining!")
                self.n_clusters = nClusters.value
                self.km = KMeans(n_clusters=self.n_clusters)
                self.km.fit_transform(self.dh.full_df[["Latitude", "Longitude"]])
                self.colours = self.generate_n_colors(self.n_clusters)
            else:
                logging.info("Not retraining")
            lon, lat = self.merc(df["Latitude"], df["Longitude"])
            source.data = dict(
                x=lon,
                y=lat,
                loc=df["Location"],
                lat=df["Longitude"],
                lon=df["Latitude"],
                amount_of_tickets=df["Exact issuing time"],
                colors_chosen=[
                    self.colours[x]
                    for x in self.km.predict(df[["Latitude", "Longitude"]])
                ],
                amt=3
                * np.log1p(df["Exact issuing time"])
                / np.min(np.log1p(df["Exact issuing time"])),
            )
            submit_button.label = "Update map"

        controls = [
            starting_date,
            ending_date,
            max_amount_of_points,
            nClusters,
            multi_select,
            submit_button,
        ]

        def update_top_bar():
            logging.info("BEFORE MINDATE")
            mindate = (
                starting_date.value
            )  # date.fromtimestamp(starting_date.value / 1e3)
            maxdate = ending_date.value  # date.fromtimestamp(ending_date.value / 1e3)
            df = self.dh.full_df
            df = df.loc[
                (df["date issued"] >= mindate)
                & (df["date issued"] <= maxdate)
                & (df.Make.isin(multi_select.value))
            ]
            self.bar_var_chosen = select_bar_variable.value
            bar_source_new, _ = self.create_bar_plot(
                self.bar_var_chosen, df, show_top.value
            )
            indices = [
                str(x) for x in list(df[self.bar_var_chosen].value_counts().index)
            ]
            bar_plot.x_range.factors = [str(x) for x in list(indices)][: show_top.value]
            bar_source.data = bar_source_new.data

        # for control in controls:
        #    control.on_change('value', lambda attr, old, new: update())
        submit_button.on_click(update)

        map_inputs = column(*controls, width=320, height=1000)
        map_inputs.sizing_mode = "fixed"
        bar_controls = [select_bar_variable, show_top]
        # for control in controls:
        #    control.on_change('value', lambda attr, old, new: update())
        select_bar_variable.on_change("value", lambda attr, old, new: update_top_bar())
        show_top.on_change("value", lambda attr, old, new: update_top_bar())
        bar_inputs = column(*bar_controls, width=320, height=1000)
        bar_inputs.sizing_mode = "fixed"
        lay_out = layout(
            [[map_inputs, p], [bar_inputs, bar_plot]], sizing_mode="scale_both"
        )
        doc.add_root(lay_out)
        doc.title = "Parking tickets in LA"
