from flask import Flask, render_template, request
import os
import numpy as np
import pandas as pd
from Modules.plotter import Plotter
from Modules.ETL.data_handler import DataHandler
from Modules.kernelized_model import KernelModel
from bokeh.embed import components
import json
import plotly
import chart_studio.plotly as py
import plotly.graph_objs as go
from bokeh.embed import server_document
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.server.server import Server
from bokeh.themes import Theme
from tornado.ioloop import IOLoop

from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature

app = Flask(__name__)
dh = DataHandler()
plotter = Plotter(dh = dh)
kern_model = KernelModel(dh=dh)
#geo_kern = KernelModel(dh=dh, kernel_cols = ["Latitude", "Longitude"])
#geo_kern.train_model()


def bkapp(doc):
    df = sea_surface_temperature.copy()
    source = ColumnDataSource(data=df)

    plot = figure(x_axis_type='datetime', y_range=(0, 25), y_axis_label='Temperature (Celsius)',
                  title="Sea Surface Temperature at 43.18, -70.43")
    plot.line('time', 'temperature', source=source)

    def callback(attr, old, new):
        if new == 0:
            data = df
        else:
            data = df.rolling('{0}D'.format(new)).mean()
        source.data = ColumnDataSource(data=data).data

    slider = Slider(start=0, end=30, value=0, step=1, title="Smoothing by N Days")
    slider.on_change('value', callback)

    doc.add_root(column(slider, plot))

    doc.theme = Theme(filename="theme.yaml")

@app.route("/densitites")
def densities():
    plot = plotter.many_densities()
    script, div = components(plot)
    return render_template("twodimhist.html", script=script, div = div, feature_names = ["latitiude","longitude"])

@app.route('/embedding', methods=['GET'])
def bkapp_page():
    script = server_document('http://localhost:5006/bkapp')
    return render_template("embed.html", script=script, template="Flask")
def bk_worker():
    # Can't pass num_procs > 1 in this configuration. If you need to run multiple
    # processes, see e.g. flask_gunicorn_embed.py
    server = Server({'/bkapp': plotter.test_hist}, io_loop=IOLoop(), allow_websocket_origin=["localhost:5000"])
    server.start()
    server.io_loop.start()

@app.route("/")
def home():
    current_feature_name = request.args.get("feature_name")
    if current_feature_name == None:
        current_feature_name = "Year"



    wday_plot = plotter.plot_bar_chart()
    script_wday, wday_div = components(wday_plot)

    yday_plot = plotter.plot_bar_chart(col = "day_of_year")
    script_yday, yday_div = components(yday_plot)

    p = plotter.plot_bar_chart(col = current_feature_name)
    script, div = components(p)

    return render_template("home.html",
                            script_wday = script_wday,
                            wday_div=wday_div,
                            script_yday=script_yday,
                            yday_div=yday_div,
                            feature_names=list(dh.full_df),
                            script_=script,
                            div_=div,
                            feature_picked=current_feature_name
                            )



@app.route('/showLineChart')
def line():
    count = 500
    xScale = np.linspace(0, 100, count)
    yScale = np.random.randn(count)

    # Create a trace
    trace = go.Scatter(
        x = xScale,
        y = yScale
    )

    data = [trace]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    #print(graphJSON)
    return render_template('show_line_chart.html',
                               graphJSON=graphJSON)

@app.route("/twodimhist")
def twodimhist():
    p = plotter.test_histogram()
    script, div = components(p)
    return render_template("twodimhist.html", script=script, div = div, feature_names = ["latitiude","longitude"])
@app.route('/geomap')
def geo_map():

    df = dh.full_df.groupby(["Latitude","Longitude"]).count().reset_index()[["Latitude","Longitude","Ticket number"]]
    df.columns = ["Latitude","Longitude","Frequency"]

    import plotly.graph_objects as go
    trace = go.Figure(go.Densitymapbox(lat=df.Latitude, lon=df.Longitude, z=df.Frequency, radius=10))
    trace.update_layout(mapbox_style="stamen-terrain", mapbox_center_lon=180)
    trace.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    data = [trace]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    #print(graphJSON)
    return render_template('geomap.html',
                               graphJSON=graphJSON)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/model")
def model():
    return "Dude, this page is not created yet"

@app.route("/heatmap")
def heatmap():
    return "Dude, this page is not created yet"

from threading import Thread
Thread(target=bk_worker).start()

if __name__ == "__main__":
    app.run(debug=True)
