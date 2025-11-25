# Assignment-8

# States Above Threshold by Month

This script processes a COVID‑19 dataset in CSV format and outputs, for each month, the list of U.S. states whose **maximum reported test results** exceeded a given threshold.

It uses only Python built‑ins (no external libraries) to:
- Parse dates into `YYYY-MM` format
- Handle CSV rows with quoted fields
- Aggregate monthly maximum values per state
- Write results to a new CSV file


## Usage

### Run the script
By default, the script runs with a threshold of **1,000,000**:

Example Output
Given a threshold of 1,000,000, the output CSV might look like:

'''
month,states,count
2020-03,NY;NJ,2
2020-04,NY;NJ;CA;IL,4
2020-05,NY;NJ;CA;IL;TX,5
'''
