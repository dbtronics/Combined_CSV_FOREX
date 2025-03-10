#!/bin/bash
# echo $base
base="$(pwd)"
destination="$HOME/Dropbox/Investments/Prop Farming/Reports/log"
# # shifts entire log files from misc to logs specific directory
cd "$destination"
bash "$destination/misc2log.sh"


cd "$destination/"
for folder in [0-9]*/; do  # picks all the folders
# for folder in 4169*/; do # picks only specific folder
#for folder in 3123*/; do # picks only specific folder
    mkdir "$base/${folder:0:4}_data"
    find "$folder" -maxdepth 1 -type f -name "*log*" -exec cp {} "$base/${folder:0:4}_data" \;

done
