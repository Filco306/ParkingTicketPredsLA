import math
from ast import literal_eval


class CoordinatesHandler:
# Fetches locations in batches

    def __init__(self, api = "MapQuest", key = None, secret = None):
        self.api = api
        self.key = key
        self.secret = secret

    def get_coordinates_from_API(locs_list, api_key = None):
        if self.api is None and api_key is None:
            raise Exception("Did not find any API key. Please try again.")


    # Completely copied from https://towardsdatascience.com/exploring-and-visualizing-chicago-transit-data-using-pandas-and-bokeh-part-ii-intro-to-bokeh-5dca6c5ced10
    # And then remade
    # Coords is a list of coordinates, right?
    def merc(self, lat, lon):
        #Coordinates = literal_eval(Coords)
        #lat = Coordinates[0]
        #lon = Coordinates[1]
        
        r_major = 6378137.000
        x = r_major * math.radians(lon)
        scale = x/lon
        y = 180.0/math.pi * math.log(math.tan(math.pi/4.0 +
            lat * (math.pi/180.0)/2.0)) * scale
        return (x, y)
