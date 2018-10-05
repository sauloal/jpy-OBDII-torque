#!/bin/bash

echo "CONVERTING CSVs"
jupyter nbconvert --stdout --execute logParserCSV.ipynb > /dev/null

echo "OPENING"
jupyter lab --no-browser --notebook-dir=. &
