import math
from src.data_handler import DataHandler
from bokeh.models import Button
from bokeh.models.widgets import Slider, Select, TableColumn, DataTable
from bokeh.models.widgets.inputs import DatePicker, MultiSelect
from datetime import datetime
import numpy as np
import pandas as pd
import os
import random
from bokeh.tile_providers import get_provider, Vendors
from bokeh.layouts import column, layout
from bokeh.models import BoxSelectTool, LassoSelectTool, ColumnDataSource
from bokeh.plotting import figure
from sklearn.cluster import KMeans
from src.db_connecting import get_postgis_conn, get_all_between_dates, get_per_location
import logging

logging.basicConfig(level=os.environ.get("LOGGING_LEVEL", "INFO"))


class Plotter:
    def __init__(self, dh=None):
        logging.info("Let's plot some stuff!")
        self.conn = get_postgis_conn()
        if dh is None:
            self.dh = DataHandler()
        else:
            self.dh = dh

    def show_table(self, doc):
        startdate = datetime(2015, 9, 16)
        enddate = datetime(2015, 9, 17)
        df = get_all_between_dates(self.conn, startdate, enddate, limit=1000)
        data = {}
        for col in df:
            data[col] = df[col]
        table_source = ColumnDataSource(data=data)
        columns = [TableColumn(field=x, title=x) for x in list(df)]
        data_table = DataTable(
            source=table_source, columns=columns, width=400, height=280
        )

        def update():
            pass

        lay_out = layout([data_table], sizing_mode="scale_both")
        logging.info(df)
        doc.add_root(lay_out)
        doc.title = "Parking tickets in LA"

    # Completely copied from
    # https://towardsdatascience.com/
    # exploring-and-visualizing-chicago
    # -transit-data-using-pandas-and-bokeh-
    # part-ii-intro-to-bokeh-5dca6c5ced10
    # And then remade
    def merc(self, lat, lon):

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
        Generates a number of colors to
        use for the different clusters when
        clustering using k-means.

    """

    def generate_n_colors(self, n):

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

        default_bar_var = "location"
        min_date = datetime(2014, 9, 16)
        max_date = datetime(2019, 9, 17)
        self.n_clusters = 4
        default_top = 10
        self.dh.full_df = get_per_location(self.conn, min_date, max_date, limit=10000)

        df = self.dh.full_df

        logging.info("Here we are now")

        logging.info("Training")
        self.km = KMeans(n_clusters=self.n_clusters)
        self.km.fit_transform(df[["latitude", "longitude"]])
        logging.info("Finished training")

        # Now: create bar chart!
        logging.info("Yes")
        bar_source, bar_plot = self.create_bar_plot(default_bar_var, df, default_top)
        self.bar_var_chosen = default_bar_var
        df = (
            df.groupby(["location", "latitude", "longitude"])
            .count()
            .reset_index()[["location", "latitude", "longitude", "freq"]]
        )
        df = df.loc[df.index < 1000]
        self.colours = self.generate_n_colors(self.n_clusters)
        TOOLS = "pan,wheel_zoom,box_select,lasso_select,reset"

        lon, lat = self.merc(df["latitude"], df["longitude"])
        logging.info(df)
        source = ColumnDataSource(
            data=dict(
                lon=df["longitude"],
                lat=df["latitude"],
                loc=df["location"],
                amount_of_tickets=df["freq"],
                colors_chosen=[
                    self.colours[x]
                    for x in self.km.predict(df[["latitude", "longitude"]])
                ],
                x=lon,
                y=lat,
                amt=3 * np.log1p(df["freq"]) / np.min(np.log1p(df["freq"])),
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
            min_date=datetime(2012, 1, 1),
            max_date=datetime.now(),
            value=min_date,
        )
        ending_date = DatePicker(
            title="Date Range: ",
            min_date=datetime(2012, 1, 1),
            max_date=datetime.now(),
            value=max_date,
        )
        limit = Slider(
            title="Maximum number of points in scatter: ",
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

        makes = pd.read_sql("SELECT DISTINCT MAKE FROM PARKINGTICKET", self.conn)
        logging.info(makes)
        multi_select = MultiSelect(
            title="Which cars makes to include:",
            value=list(makes.make.value_counts().index),
            options=list(makes.make.value_counts().index),
        )

        select_bar_variable = Select(
            title="",
            value=default_bar_var,
            options=[
                ("make", "make"),
                ("Violation Description", "Violation Description"),
                ("Agency", "Agency"),
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
            mindate = starting_date.value
            maxdate = ending_date.value
            self.dh.full_df = get_per_location(
                self.conn, mindate, maxdate, limit=limit.value
            )
            df = self.dh.full_df
            if df.shape[0] == 0:
                logging.warning(
                    "DF is empty!!! Adding dummy data to cover up for now. "
                )
                self.dh.full_df = pd.read_sql(
                    """SELECT location,
                       AVG(latitude) as latitude,
                       AVG(longitude) as longitude,
                       count(*) as freq
                FROM parkingticket
                group by location
                ORDER BY freq DESC
                LIMIT 10;""",
                    self.conn,
                )
                df = self.dh.full_df
            self.bar_var_chosen = select_bar_variable.value
            bar_source_new, _ = self.create_bar_plot(
                self.bar_var_chosen, df, show_top.value
            )
            indices = [
                str(x) for x in list(df[self.bar_var_chosen].value_counts().index)
            ]
            bar_plot.x_range.factors = [str(x) for x in list(indices)][: show_top.value]
            df = (
                df.groupby(["location", "latitude", "longitude"])
                .count()
                .reset_index()
                .sort_values(by="freq", ascending=False)
            )
            return (
                bar_source_new,
                df.loc[
                    df.index < limit.value,
                    ["location", "latitude", "longitude", "freq"],
                ],
            )

        def update():
            submit_button.label = "Updating..."
            logging.info("In update")
            # TODO: Only update if make, min_date or max_date is changed
            bar_source_new, df = select_data()

            # TODO: Do not re-render each time

            bar_source.data = bar_source_new.data

            logging.info("DF should be changed?")
            logging.info(df)
            logging.info(df.shape)
            if nClusters.value != self.n_clusters:  # then retrain!
                logging.info("Retraining!")
                self.n_clusters = nClusters.value
                self.km = KMeans(n_clusters=self.n_clusters)
                self.km.fit_transform(self.dh.full_df[["latitude", "longitude"]])
                self.colours = self.generate_n_colors(self.n_clusters)
            else:
                logging.info("Not retraining")
            lon, lat = self.merc(df["latitude"], df["longitude"])
            source.data = dict(
                x=lon,
                y=lat,
                loc=df["location"],
                lat=df["longitude"],
                lon=df["latitude"],
                amount_of_tickets=df["freq"],
                colors_chosen=[
                    self.colours[x]
                    for x in self.km.predict(df[["latitude", "longitude"]])
                ],
                amt=3 * np.log1p(df["freq"]) / np.min(np.log1p(df["freq"])),
            )
            submit_button.label = "Update map"

        controls = [
            starting_date,
            ending_date,
            limit,
            nClusters,
            multi_select,
            submit_button,
        ]

        def update_top_bar():
            logging.info("BEFORE MINDATE")
            # mindate = starting_date.value
            # maxdate = ending_date.value
            df = self.dh.full_df
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
