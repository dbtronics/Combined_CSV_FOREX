#!/bin/bash

rm -dr *data
base="$(pwd)"

destination="$HOME/Dropbox/Investments/Prop Farming/Reports/log"


for input in [0-9]*; do
    if [[ -f $input ]]; then
        destination_data_folder=$(find "$destination" -type d -name "${input:0:4}*" | head -n 1) # Find the folder matching the pattern
        echo $destination_data_folder
        mv ${input:0:4}* "$destination_data_folder/"        
        mv "$destination_data_folder"/*log* "$destination_data_folder/Archive/"
    fi

done

cd "$destination"
bash "$destination/log2archive.sh"