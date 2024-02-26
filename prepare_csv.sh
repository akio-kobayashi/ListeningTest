#!/bin/bash

for NUM in 01 02 03 04 05 06 07 08 09 10 11 12;do
    find ./reference/聴取実験-${NUM}/ -name \*wav|python3 prepare_csv.py --output csv/test_${NUM}.csv
done
