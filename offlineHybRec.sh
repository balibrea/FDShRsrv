#!/bin/bash
# Usage: ./offlinereconstr.sh YYYY-MM-DD
# Example: ./offlinereconstr.sh 2025-08-21

set -e  # exit on error

if [ $# -ne 1 ]; then
    echo "Usage: $0 YYYY-MM-DD"
    exit 1
fi

DATE=$1
Y=$(date -d "$DATE" +%Y)
M=$(date -d "$DATE" +%m)
D=$(date -d "$DATE" +%d)

HOME_DIR=$HOME/offline/HdDataReconstruction
CURRENT_DIR=$HOME/CurrentShift

# Generate EventFileReader.xml from template
# set the day to be analyzed on file
sed 's/YYYY\/MM\/hd_YYYY_MM_DD/'${Y}'\/'${M}'\/hd_'${Y}'_'${M}'_'${D}'/g' $HOME/offline/HdDataReconstruction/EventFileReader.xml.patern > $HOME/offline/HdDataReconstruction/EventFileReader.xml

if [ $? != 0 ]; then
  echo "error in EventFileReader.xml.patern file, please check it manually!"
  exit 1
fi

# Load environment
source $HOME/offline/setvars.sh

# Go to reconstruction directory
cd $HOME_DIR

# Run offline reconstruction
./userAugerOffline |& tee log_hyb_${Y}_${M}_${D}.log

# Move results to CurrentShift
mv $HOME_DIR/ADST.root $CURRENT_DIR/ADST_hyb_${Y}_${M}_${D}.root
mv $HOME_DIR/log_hyb_${Y}_${M}_${D}.log $CURRENT_DIR/

echo "Reconstruction for $DATE completed!"