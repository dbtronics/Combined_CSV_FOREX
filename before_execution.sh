#!/bin/bash

destination="/Users/dianbasit/Dropbox/Investments/Prop Farming/Reports/log"
base="/Users/dianbasit/Dropbox/Investments/Prop Farming/EAs/Dian-EAs/GitHub Data/Combined_CSV_FOREX"

cd "$destination/"
for folder in [0-9]*/; do 
mkdir "$base/${folder:0:4}_data"
find "$folder" -maxdepth 1 -type f -name "*log*" -exec cp {} "$base/${folder:0:4}_data" \;

done
