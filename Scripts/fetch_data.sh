#!/bin/sh
echo "Downloading datasets"
cat ~/.kaggle/kaggle.json
kaggle datasets download -d cityofLA/los-angeles-parking-citations
echo "Unzipping"
unzip los-angeles-parking-citations
rm los-angeles-parking-citations.zip
rm $pdf_file_name #LADOT\-Xerox\ Crib\ Sheet\ Agency\ Codes\ 12\-31\-2015\ \(1\).pdf
# Is the data removed yet? No
rm Data/parking-citations.csv
# Now yes
mv parking-citations.csv Data/ # move csv to Data/ folder
mv socrata_metadata.json metadata_parking_tickets.json
mv metadata_parking_tickets.json Data/MetaData/
# Fetching the addresses
kaggle datasets download -d cityofLA/los-angeles-addresses
unzip los-angeles-addresses.zip
mv addresses-in-the-city-of-los-angeles.csv Data/
mv socrata_metadata.json metadata_addresses.json
mv metadata_addresses.json Data/MetaData/
# Data should now be prepared. Now process it?
