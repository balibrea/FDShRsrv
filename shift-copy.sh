#!/bin/bash

# Yosel de Jesus Balibrea Lastre
# 2025-07-16
# Script to copy files from ~/CurrentShift to ~/PreviousShifts/START_DATE-ADST
# based on a date range provided as arguments.
# Files are identified by the date pattern YYYY_MM_DD in their filenames.

# Usage: ./copy_files_by_date.sh START_DATE END_DATE
# Example: ./copy_files_by_date.sh 2025-07-16 2025-07-20

SRC_DIR=~/CurrentShift
START_DATE=$1   # format YYYY-MM-DD
END_DATE=$2     # format YYYY-MM-DD

if [ $# -ne 2 ]; then
    echo "Usage: $0 START_DATE END_DATE"
    exit 1
fi

# Check date format (YYYY-MM-DD)
if ! date -d "$START_DATE" "+%Y-%m-%d" >/dev/null 2>&1; then
    echo "Error: START_DATE '$START_DATE' is not a valid date (YYYY-MM-DD)."
    exit 1
fi
if ! date -d "$END_DATE" "+%Y-%m-%d" >/dev/null 2>&1; then
    echo "Error: END_DATE '$END_DATE' is not a valid date (YYYY-MM-DD)."
    exit 1
fi

# Check start date <= end date
if [ "$(date -d "$START_DATE" +%s)" -gt "$(date -d "$END_DATE" +%s)" ]; then
    echo "Error: START_DATE cannot be after END_DATE."
    exit 1
fi

# Destination folder based on start date
DST_DIR=~/PreviousShifts/${START_DATE}-ADST
mkdir -p "$DST_DIR"

current_date="$START_DATE"
while [ "$(date -d "$current_date" +%Y-%m-%d)" != "$(date -d "$END_DATE + 1 day" +%Y-%m-%d)" ]; do
    ymd=$(date -d "$current_date" +%Y_%m_%d)

    # Copy all files matching the date pattern
    for f in "$SRC_DIR"/*"$ymd"*; do
        if [ -f "$f" ]; then
            echo "Copying $f -> $DST_DIR"
            cp "$f" "$DST_DIR/"
            rm "$f"  # Remove original file after copying
        fi
    done

    # Next day
    current_date=$(date -I -d "$current_date + 1 day")
done

echo "✅ Files copied to $DST_DIR"
# End of script