#!/bin/bash

rm -dr *data

# destination="/Users/dianbasit/Dropbox/Investments/Prop Farming/Reports/log"
# base="/Users/dianbasit/Dropbox/Investments/Prop Farming/EAs/Dian-EAs/GitHub Data/Combined_CSV_FOREX"
destination="/Users/sulemanbasit/Dropbox/Investments/Prop Farming/Reports/log"
base="/Users/sulemanbasit/Dropbox/Investments/Prop Farming/EAs/Dian-EAs/GitHub Data/Combined_CSV_FOREX"

for input in [0-9]*; do
    if [[ -f $input ]]; then
        destination_data_folder=$(find "$destination" -type d -name "${input:0:4}*" | head -n 1) # Find the folder matching the pattern
        echo $destination_data_folder
        mv ${input:0:4}* "$destination_data_folder/"        
        mv "$destination_data_folder"/*log* "$destination_data_folder/Archive/"
    fi

done

cd "/Users/sulemanbasit/Dropbox/Investments/Prop Farming/Reports/log/"
bash "/Users/sulemanbasit/Dropbox/Investments/Prop Farming/Reports/log/log2archive.sh"