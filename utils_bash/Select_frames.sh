#######################
#  Created on: May 16, 2024
#  Author: Adriana GV
#######################

#!/bin/bash

# Path where the frames are
if [ $# -ne 1 ]; then
    echo "A path is needed, follow the example:"
    echo "Example: $0 <frames_path>"
    exit 1
fi
frames_path="$1"
if [ ! -d "$frames_path" ]; then
    echo "The specified directory does not exist."
    exit 1
fi

files=$(ls -t "$frames_path"/*.png)

# Counter
count=0
for file in $files; do
    if [ $count -eq 5 ]; then
        count=0
    else
        rm "$file"
        echo "Removed: $file"
        count=$((count + 1))
    fi
done