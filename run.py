from flask import Flask, render_template, request, jsonify
from src.plotter import Plotter
from bokeh.embed import components
from bokeh.embed import server_document
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.server.server import Server
from bokeh.themes import Theme
from tornado.ioloop import IOLoop
from threading import Thread
from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature

app = Flask(__name__)
plotter = Plotter(dh=None)


def bkapp(doc):
    df = sea_surface_temperature.copy()
    source = ColumnDataSource(data=df)

    plot = figure(
        x_axis_type="datetime",
        y_range=(0, 25),
        y_axis_label="Temperature (Celsius)",
        title="Sea Surface Temperature at 43.18, -70.43",
    )
    plot.line("time", "temperature", source=source)

    def callback(attr, old, new):
        if new == 0:
            data = df
        else:
            data = df.rolling("{0}D".format(new)).mean()
        source.data = ColumnDataSource(data=data).data

    slider = Slider(start=0, end=30, value=0, step=1, title="Smoothing by N Days")
    slider.on_change("value", callback)

    doc.add_root(column(slider, plot))

    doc.theme = Theme(filename="theme.yaml")


@app.route("/densitites")
def densities():
    plot = plotter.many_densities()
    script, div = components(plot)
    return render_template(
        "twodimhist.html",
        script=script,
        div=div,
        feature_names=["latitiude", "longitude"],
    )


@app.route("/map", methods=["GET"])
def map_page():
    script = server_document("http://localhost:5006/map")
    return render_template("embed.html", script=script, template="Flask")


@app.route("/table", methods=["GET"])
def table_page():
    script = server_document("http://localhost:5006/table")
    return render_template("embed.html", script=script, template="Flask")


def bk_worker():
    # Can't pass num_procs > 1 in this configuration.
    # If you need to run multiple
    # processes, see e.g. flask_gunicorn_embed.py
    server = Server(
        {"/table": plotter.show_table, "/map": plotter.test_hist},
        io_loop=IOLoop(),
        allow_websocket_origin=["localhost:5000"],
    )
    server.start()
    server.io_loop.start()


@app.route("/")
def home():
    current_feature_name = request.args.get("feature_name")
    if current_feature_name is None:
        current_feature_name = "Year"

    wday_plot = plotter.plot_bar_chart()
    script_wday, wday_div = components(wday_plot)

    yday_plot = plotter.plot_bar_chart(col="day_of_year")
    script_yday, yday_div = components(yday_plot)

    p = plotter.plot_bar_chart(col=current_feature_name)
    script, div = components(p)

    return render_template(
        "home.html",
        script_wday=script_wday,
        wday_div=wday_div,
        script_yday=script_yday,
        yday_div=yday_div,
        script_=script,
        div_=div,
        feature_picked=current_feature_name,
    )


@app.route("/twodimhist")
def twodimhist():
    p = plotter.test_hist()
    script, div = components(p)
    return render_template(
        "twodimhist.html",
        script=script,
        div=div,
        feature_names=["latitiude", "longitude"],
    )


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/health")
def health():
    return jsonify({"status": "200 OK"})


@app.route("/model")
def model():
    return "Dude, this page is not created yet"


@app.route("/heatmap")
def heatmap():
    return "Dude, this page is not created yet"


Thread(target=bk_worker).start()

if __name__ == "__main__":
    app.run(debug=True)
