#!/bin/bash

# Usage: ./process_dates.sh 2025-08-17 2025-08-20

START_DATE=2025-08-14
END_DATE=2025-08-17

INPUT_BASE="/Raid/data/Prod/v2r0/Hybrid"
OUTPUT_DIR="/home/auger/CurrentShift"

mkdir -p "$OUTPUT_DIR"

# Convert dates to seconds since epoch
start_ts=$(date -d "$START_DATE" +%s)
end_ts=$(date -d "$END_DATE" +%s)

# Number of days to process
days=$(( (end_ts - start_ts) / 86400 ))

for i in $(seq 0 $days); do
    current_date=$(date -d "$START_DATE + $i day" +%Y-%m-%d)
    YEAR=$(date -d "$current_date" +%Y)
    MONTH=$(date -d "$current_date" +%m)
    DAY=$(date -d "$current_date" +%d)

    INPUT_FILE="$INPUT_BASE/$YEAR/$MONTH/hd_${YEAR}_${MONTH}_${DAY}_12h00.root"
    OUTPUT_FILE="$OUTPUT_DIR/ADST_hyb_${YEAR}_${MONTH}_${DAY}.root"

    echo "Checking $INPUT_FILE"

    if [ -f "$INPUT_FILE" ]; then
        if [ -f "$OUTPUT_FILE" ]; then
            echo " → Output exists: $OUTPUT_FILE (skipping)"
        else
            echo " → Processing $INPUT_FILE → $OUTPUT_FILE"
            # Replace this with your real computation command:
            #process_file "$INPUT_FILE" "$OUTPUT_FILE"
        fi
    else
        echo " → Input not found: $INPUT_FILE"
    fi
done
