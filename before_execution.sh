#!/bin/bash

# shifts entire log files from misc to logs specific directory
cd "/Users/sulemanbasit/Dropbox/Investments/Prop Farming/Reports/log/"
bash "/Users/sulemanbasit/Dropbox/Investments/Prop Farming/Reports/log/misc2log.sh"

# destination="/Users/dianbasit/Dropbox/Investments/Prop Farming/Reports/log"
# base="/Users/dianbasit/Dropbox/Investments/Prop Farming/EAs/Dian-EAs/GitHub Data/Combined_CSV_FOREX"
destination="/Users/sulemanbasit/Dropbox/Investments/Prop Farming/Reports/log"
base="/Users/sulemanbasit/Dropbox/Investments/Prop Farming/EAs/Dian-EAs/GitHub Data/Combined_CSV_FOREX"

cd "$destination/"
for folder in [0-9]*/; do  # picks all the folders
# for folder in 4169*/; do # picks only specific folder
#for folder in 3123*/; do # picks only specific folder
    mkdir "$base/${folder:0:4}_data"
    find "$folder" -maxdepth 1 -type f -name "*log*" -exec cp {} "$base/${folder:0:4}_data" \;

done
