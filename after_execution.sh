#!/bin/bash

rm -dr *data

destination="/Users/dianbasit/Dropbox/Investments/Prop Farming/Reports/log"
base="/Users/dianbasit/Dropbox/Investments/Prop Farming/EAs/Dian-EAs/GitHub Data/Combined_CSV_FOREX"

for input in [0-9]*; do
if [[ -f $input ]]; then
mv ${input:0:4}* "$destination"               
fi
done

