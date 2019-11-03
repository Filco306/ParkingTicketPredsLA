import numpy as np

import pandas as pd

data = pd.read_csv("Data/parking-citations.csv")
data.head()

df = data
del data
df = df.drop_duplicates("Ticket number")
df.isna().sum()
# Fill all Latitude and longitude with bad values
df[['Latitude','Longitude']] = df[['Latitude','Longitude']].fillna(99999.0)

df.loc[df.Latitude == 99999.0].shape
# 1446794 are real bad then.


df.shape

# Drop all without Issue Date and Issue Time
df = df.dropna(subset=["Issue Date", "Issue time"],axis = 0)
df = df.loc[(df.Location.isna() == False) | (df.Latitude != 99999.0)]

df.shape
df.Latitude.value_counts().sort_values()
df.Longitude.value_counts().sort_values()



#df.Longitude.value_counts().sort_values().reset_index()['index'].apply(lambda x : x/100000)
#df.Latitude.value_counts().sort_values().reset_index()['index'].apply(lambda x : x/100000)


from pyproj import Proj, transform
# coords are in x/y and we want lat/long, this is from the pyproj documentation
pm = '+proj=lcc +lat_1=34.03333333333333 +lat_2=35.46666666666667 +lat_0=33.5 +lon_0=-118 +x_0=2000000 ' \
     '+y_0=500000.0000000002 +ellps=GRS80 +datum=NAD83 +to_meter=0.3048006096012192 +no_defs'

# convert to lat/long
x_in,y_in = df['Latitude'].values, df['Longitude'].values
lat,long = transform(Proj(pm, preserve_units = True), Proj("+init=epsg:4326"), x_in,y_in)
df['Latitude'] = lat
df['Longitude'] = long

df['Latitude'].max()
df['Latitude'].min()
df['Longitude'].max()
df['Longitude'].min()

df.Latitude.value_counts().index[0]
df.Longitude.value_counts().index[0]



locs_to_fetch = df.loc[(df.Latitude == df.Latitude.value_counts().index[0]) | (df.Longitude == df.Longitude.value_counts().index[0]),["Ticket number","Location"]]
locs_to_fetch.Location = locs_to_fetch.Location.apply(lambda x : x+" los angeles")
list(locs_to_fetch)

verizon_key = "fIZKJwtMQeBDDMDbfIYGwmfdI1TXuLgy"
bBox = "boundingBox=-119.492534399,33.3113522026,-116.9065415859,34.8462036835"
url = "http://www.mapquestapi.com/geocoding/v1/batch?key="+verizon_key+"&"+bBox+"&"
list(locs_to_fetch.Location)[:100]

import requests
import json
loc = []
lats = []
longs = []
for i in np.arange(100,locs_to_fetch.shape[0],100):
    r = requests.get(url+"&location="+"&location=".join(list(locs_to_fetch.Location)[(i-100):i]))
    j = json.loads(r.text)
    for i in j['results']:
        print("loc: {}, lat: {}, long: {}".format(i['providedLocation']['location'],i['locations'][0]['latLng']['lat'],i['locations'][0]['latLng']['lng']))
        loc.append(i['providedLocation']['location'])
        lats.append(i['locations'][0]['latLng']['lat'])
        longs.append(i['locations'][0]['latLng']['lng'])

new_locs = pd.DataFrame([loc,lats,longs]).T
new_locs.columns = ['Location','Latitude','Longitude']
locs_to_fetch.merge(new_locs, on = "Location")


new_locs
new_locs = new_locs.drop_duplicates()

new_locs.Location = new_locs.Location.str.replace(" los angeles",'')

new_coords = df[['Ticket number','Location']].merge(new_locs, on = "Location")


# Time to

def root_nested(df, col1 = "Ticket number", col2 = "Latitude", col1_val, col2_val):
    df['col1'] = np.where(df['col1'] == 0, np.where(df['col2'] == 0, df['col3'], df['col2']), df['col1'])
    return df


np.where(df['Ticket number'] == 4359662414,
                      np.where(df['col2'] == 0, df['col3'], df['col2']),
                      df['col1'])

df = df.merge(new_coords.drop("Location",axis = 1), how='left',on='Ticket number')





df.to_pickle("Data/parking_tickets_more_updated_coordinates")
