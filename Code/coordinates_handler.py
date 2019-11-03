


class CoordinatesHandler:
# Fetches locations in batches

    def __init__(self, api = "MapQuest", key = None, secret = None):
        self.api = api
        self.key = key
        self.secret = secret

    def get_coordinates_from_API(locs_list, api_key = None):
        if self.api is None and api_key is None:
            raise Exception("Did not find any API key. Please try again.")
    
    def convert_coordinates(self,latitudes,longitudes):
