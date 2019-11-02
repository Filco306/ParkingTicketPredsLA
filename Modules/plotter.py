import bokeh
import pandas as pd
from Modules.data_handler import DataHandler
from bokeh.plotting import figure
class Plotter:
    def __init__(self,dh = None):
        # Let's plot!
        # Check this out https://plot.ly/python/filled-area-on-mapbox/
        print("Let's plot some stuff!")
        if dh is None:
            self.dh = DataHandler()
        else:
            self.dh = dh

        # Load data for plotting



    def plot_heatmap(self):
        print("Plotting heatmap")
        from bokeh.plotting import figure


    def plot_fruits(self, col = "day_of_week"):
        print("Plotting bar chart with "+col)

        fruits = ['Apples', 'Pears', 'Nectarines', 'Plums', 'Grapes', 'Strawberries']

        p = figure(x_range=fruits, plot_height=250, title="Fruit Counts")
        p.vbar(x=fruits, top=[5, 3, 4, 2, 4, 6], width=0.9)

        p.xgrid.grid_line_color = None
        p.y_range.start = 0
        return p


    def plot_line_chart(self, df = None, col = "Frequency"):
        if df is None:
            df = dh.full_df



    def plot_bar_chart(self, col = "day_of_week"):
        print("Plotting bar chart with "+col)
        c = self.dh.full_df[col]

        indices = c.value_counts().sort_index().index
        #fruits = ['Apples', 'Pears', 'Nectarines', 'Plums', 'Grapes', 'Strawberries']
        print(c.value_counts().sort_index().values)
        p = figure(x_range=[str(x) for x in list(indices)], plot_height=250, title=col)
        p.vbar(x=indices+0.5, top=c.value_counts().sort_index().values, width=0.9)

        p.xgrid.grid_line_color = None
        p.y_range.start = 0
        return p
