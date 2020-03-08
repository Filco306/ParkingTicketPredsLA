#!/bin/sh
echo "Downloading datasets"
mkdir Data
mkdir Data/MetaData
mkdir Data/processed_data
chmod 600 ~/.kaggle/kaggle.json
cat ~/.kaggle/kaggle.json
kaggle datasets download -d cityofLA/los-angeles-parking-citations
echo "Unzipping"
unzip los-angeles-parking-citations
rm los-angeles-parking-citations.zip
# Is the data removed yet? No
rm Data/parking-citations.csv
# Now yes
mv parking-citations.csv Data/ # move csv to Data/ folder
mv socrata_metadata.json metadata_parking_tickets.json
mv metadata_parking_tickets.json Data/MetaData/
# Fetching the addresses
kaggle datasets download -d cityofLA/los-angeles-addresses
unzip los-angeles-addresses.zip
rm los-angeles-addresses.zip
mv addresses-in-the-city-of-los-angeles.csv Data/addresses-in-the-city-of-los-angeles.csv
mv socrata_metadata.json metadata_addresses.json
mv metadata_addresses.json Data/MetaData/
# Data should now be prepared. Now process it?
python3 -u ./index.py
