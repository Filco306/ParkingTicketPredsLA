from flask import Flask, render_template, request
import os
import numpy as np
import pandas as pd
from Modules.plotter import Plotter
from Modules.data_handler import DataHandler
from Modules.kernelized_model import KernelModel
from bokeh.embed import components
import json
import plotly
import chart_studio.plotly as py
import plotly.graph_objs as go

app = Flask(__name__)
dh = DataHandler()
plotter = Plotter(dh = dh)
kern_model = KernelModel(dh=dh)
#geo_kern = KernelModel(dh=dh, kernel_cols = ["Latitude", "Longitude"])
#geo_kern.train_model()




@app.route("/")
def home():
    current_feature_name = request.args.get("feature_name")
    if current_feature_name == None:
        current_feature_name = "Year"
    plot = plotter.plot_fruits()
    script_, fruit_div = components(plot)

    wday_plot = plotter.plot_bar_chart()
    script_wday, wday_div = components(wday_plot)

    yday_plot = plotter.plot_bar_chart(col = "day_of_year")
    script_yday, yday_div = components(yday_plot)

    p = plotter.plot_bar_chart(col = current_feature_name)
    script, div = components(p)

    return render_template("home.html",
                            script_fruit_bars = script_,
                            fruit_div=fruit_div,
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

if __name__ == "__main__":
    app.run(debug=True)
