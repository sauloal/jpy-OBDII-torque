#!/bin/bash

echo "CONVERTING CSVs"
jupyter nbconvert --stdout --execute logParser.ipynb > /dev/null

echo "OPENING"
jupyter notebook --no-browser --notebook-dir=. &
