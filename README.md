# pycot

pycot is a easy to use python library for interacting with the [CFTC Commitment of Traders](https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm) reports.

## Installation

```ini
pip install pycot-reports
```

## Requirements

* pandas
* requests

## How to use

```python
from pycot import legacy_report, disaggregated_report, financial_report
```

Lets have a look at an example.

### Legacy Report

```python
from pycot import legacy_report
contract_name = ("FED FUNDS - CHICAGO BOARD OF TRADE", "30-DAY FEDERAL FUNDS - CHICAGO BOARD OF TRADE")
df = legacy_report("legacy_fut", contract_name)
```

Output Example:

```ini
                                            Contract Name  Open Interest  ...  Net Change, Large Spec  Net % of OI, Large Spec
Date                                                                      ...                                                 
2023-05-30             FED FUNDS - CHICAGO BOARD OF TRADE      1855851.0  ...                -91660.0                     -9.7
2023-05-23             FED FUNDS - CHICAGO BOARD OF TRADE      1735674.0  ...                -20924.0                     -5.1
2023-05-16             FED FUNDS - CHICAGO BOARD OF TRADE      1585578.0  ...                  7746.0                     -4.3
2023-05-09             FED FUNDS - CHICAGO BOARD OF TRADE      1502281.0  ...                -35180.0                     -5.0
2023-05-02             FED FUNDS - CHICAGO BOARD OF TRADE      1483670.0  ...                 50471.0                     -2.7
...                                                   ...            ...  ...                     ...                      ...
1993-03-23  30-DAY FEDERAL FUNDS - CHICAGO BOARD OF TRADE        11298.0  ...                   106.0                      9.1
1993-03-16  30-DAY FEDERAL FUNDS - CHICAGO BOARD OF TRADE        11015.0  ...                    -8.0                      8.3
1993-03-09  30-DAY FEDERAL FUNDS - CHICAGO BOARD OF TRADE        10651.0  ...                   -51.0                      8.8
1993-03-02  30-DAY FEDERAL FUNDS - CHICAGO BOARD OF TRADE        10902.0  ...                  -190.0                      9.0
1993-02-23  30-DAY FEDERAL FUNDS - CHICAGO BOARD OF TRADE        12460.0  ...                   -83.0                      9.4
...
```

## Contract Names

The only tricky part is the contract name.

You can find the contract name in the [CFTC Commitment of Traders](https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm) reports. The contract name is the first column in the report.

## Release Shedule

The CFTC [releases](https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm) the reports every Friday at 3:30pm Eastern Time.
