# pycot

[![PyPI version](https://d25lcipzij17d.cloudfront.net/badge.svg?id=py&r=r&ts=1683906897&type=6e&v=0.1.2&x2=0)](https://badge.fury.io/py/pycot-reports)
[![License: MIT](https://img.shields.io/badge/License-MIT-red.svg)](https://github.com/philsv/pycot/blob/main/LICENSE)
[![Weekly Downloads](https://static.pepy.tech/personalized-badge/pycot-reports?period=week&units=international_system&left_color=grey&right_color=blue&left_text=downloads/week)](https://pepy.tech/project/pycot-reports)
[![Monthly Downloads](https://static.pepy.tech/personalized-badge/pycot-reports?period=month&units=international_system&left_color=grey&right_color=blue&left_text=downloads/month)](https://pepy.tech/project/pycot-reports)
[![Downloads](https://static.pepy.tech/personalized-badge/pycot-reports?period=total&units=international_system&left_color=grey&right_color=blue&left_text=downloads)](https://pepy.tech/project/pycot-reports)

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
from pycot.reports import CommitmentsOfTraders

cot = CommitmentsOfTraders("legacy_fut")
df = cot.report(("FED FUNDS - CHICAGO BOARD OF TRADE", "30-DAY FEDERAL FUNDS - CHICAGO BOARD OF TRADE"))
```

## How do I get cached results?

If you want to retrieve data from the same report multiple times, you can use the `report` function. This will cache the results of the previous function call.

Lets have a look at an example:

```python
from pycot.reports import CommitmentsOfTraders

cot = CommitmentsOfTraders("legacy_fut")

# will load the full report (~ 10-20 seconds)
fed_funds_df = cot.report(("FED FUNDS - CHICAGO BOARD OF TRADE", "30-DAY FEDERAL FUNDS - CHICAGO BOARD OF TRADE"))

# cached, will load instantly
bbg_df = cot.report(("BBG COMMODITY - CHICAGO BOARD OF TRADE", "BLOOMBERG COMMODITY INDEX - CHICAGO BOARD OF TRADE"))
```

## Report Types

### Legacy Report (All Contracts)

```python
from pycot.reports import CommitmentsOfTraders

cot = CommitmentsOfTraders("legacy_fut")
contract_names = ("FED FUNDS - CHICAGO BOARD OF TRADE", "30-DAY FEDERAL FUNDS - CHICAGO BOARD OF TRADE")
df = cot.report(contract_names)
```

Output Example:

```ini
                                            Contract Name  Open Interest  ...  Net Change, Large Spec  Net % of OI, Large Spec
Date                                                                      ...                                                                                                                                  
2023-07-11             FED FUNDS - CHICAGO BOARD OF TRADE      1440370.0  ...                -58101.0                    -11.5
2023-07-03             FED FUNDS - CHICAGO BOARD OF TRADE      1414525.0  ...                -17553.0                     -7.5
2023-06-27             FED FUNDS - CHICAGO BOARD OF TRADE      1746984.0  ...                 12437.0                     -5.1
2023-06-20             FED FUNDS - CHICAGO BOARD OF TRADE      1693141.0  ...                 84512.0                     -6.0
2023-06-13             FED FUNDS - CHICAGO BOARD OF TRADE      1556681.0  ...                 60704.0                    -12.0
...                                                   ...            ...  ...                     ...                      ...
1993-03-23  30-DAY FEDERAL FUNDS - CHICAGO BOARD OF TRADE        11298.0  ...                   106.0                      9.1
1993-03-16  30-DAY FEDERAL FUNDS - CHICAGO BOARD OF TRADE        11015.0  ...                    -8.0                      8.3
1993-03-09  30-DAY FEDERAL FUNDS - CHICAGO BOARD OF TRADE        10651.0  ...                   -51.0                      8.8
1993-03-02  30-DAY FEDERAL FUNDS - CHICAGO BOARD OF TRADE        10902.0  ...                  -190.0                      9.0
1993-02-23  30-DAY FEDERAL FUNDS - CHICAGO BOARD OF TRADE        12460.0  ...                   -83.0                      9.4
...
```

### Disaggregated Report (Commodities)

```python
from pycot.reports import CommitmentsOfTraders

cot = CommitmentsOfTraders("disaggregated_futopt")
contract_names = ("BRENT LAST DAY - NEW YORK MERCANTILE EXCHANGE", "BRENT CRUDE OIL LAST DAY - NEW YORK MERCANTILE EXCHANGE")
df = cot.report(contract_names)
```

Output Example:

```ini
                                                Contract Name  Open Interest   ...  Net Change Managed Money  Net % of OI Managed Money
Date                                                                           ...                                                                                                                            
2023-07-11      BRENT LAST DAY - NEW YORK MERCANTILE EXCHANGE       138358.0   ...                  -2134.0                        -2.9
2023-07-03      BRENT LAST DAY - NEW YORK MERCANTILE EXCHANGE       130715.0   ...                   9436.0                        -1.4
2023-06-27      BRENT LAST DAY - NEW YORK MERCANTILE EXCHANGE       153190.0   ...                  -6135.0                        -7.4
2023-06-20      BRENT LAST DAY - NEW YORK MERCANTILE EXCHANGE       148800.0   ...                   2367.0                        -3.5
2023-06-13      BRENT LAST DAY - NEW YORK MERCANTILE EXCHANGE       147598.0   ...                  -3872.0                        -5.1
...                                                       ...            ...                            ...                         ...
2011-04-12  BRENT CRUDE OIL LAST DAY - NEW YORK MERCANTILE...        20546.0   ...                   -484.0                        17.1
2011-04-05  BRENT CRUDE OIL LAST DAY - NEW YORK MERCANTILE...        19533.0   ...                    655.0                        20.4
2011-03-29  BRENT CRUDE OIL LAST DAY - NEW YORK MERCANTILE...        18178.0   ...                   -276.0                        18.4
2011-03-15  BRENT CRUDE OIL LAST DAY - NEW YORK MERCANTILE...        20233.0   ...                    231.0                        17.9
2011-03-08  BRENT CRUDE OIL LAST DAY - NEW YORK MERCANTILE...        19639.0   ...                      NaN                        17.3
...
```

### Financial Report (Financial Instruments)

```python
from pycot.reports import CommitmentsOfTraders

cot = CommitmentsOfTraders("traders_in_financial_futures_fut")
contract_names = ("UST 10Y NOTE - CHICAGO BOARD OF TRADE", "10-YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF TRADE", "10 YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF TRADE")
df = cot.report(contract_names)
```

Output Example:

```ini
                                                Contract Name  Open Interest   ...  Net Change Lev Money  Net % of OI Lev Money
Date                                                                           ...                                                                                        
2023-07-11              UST 10Y NOTE - CHICAGO BOARD OF TRADE      4800091.0   ...              155532.0                  -26.8
2023-07-03              UST 10Y NOTE - CHICAGO BOARD OF TRADE      4737762.0   ...                7710.0                  -30.4
2023-06-27              UST 10Y NOTE - CHICAGO BOARD OF TRADE      4663919.0   ...              -51457.0                  -31.1
2023-06-20              UST 10Y NOTE - CHICAGO BOARD OF TRADE      4641767.0   ...              -53136.0                  -30.2
2023-06-13              UST 10Y NOTE - CHICAGO BOARD OF TRADE      4619668.0   ...               69602.0                  -29.1
...                                                       ...            ...   ...                   ...                    ...
2006-07-11  10-YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF...      2112145.0   ...               28199.0                    1.8
2006-07-03  10-YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF...      2136459.0   ...              -18122.0                    0.5
2006-06-27  10-YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF...      2194364.0   ...               13929.0                    1.3
2006-06-20  10-YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF...      2097072.0   ...              -27203.0                    0.6
2006-06-13  10-YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF...      1912279.0   ...                   NaN                    2.2
...
```

## List Available Contracts

```python
from pycot.reports import CommitmentsOfTraders

cot = CommitmentsOfTraders("legacy_fut")
contracts: np.ndarray = cot.list_available_contracts()
```

Output Example:

```python
array(['1-MONTH SOFR - CHICAGO MERCANTILE EXCHANGE',
       '10 YEAR DELIVERABLE IR - CHICAGO BOARD OF TRADE',
       '10 YEAR DELIVERABLE IR SWAP - CHICAGO BOARD OF TRADE',
       '10 YEAR ERIS SOFR SWAP - CHICAGO BOARD OF TRADE',
       '10 YEAR ERIS SWAP  - CHICAGO BOARD OF TRADE',
       '10-YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF TRADE',
        ...
       'UST 10Y NOTE - CHICAGO BOARD OF TRADE',
       'UST 2Y NOTE - CHICAGO BOARD OF TRADE',
       'UST 5Y NOTE - CHICAGO BOARD OF TRADE',
       'UST BOND - CHICAGO BOARD OF TRADE',
       'VIX FUTURES - CBOE FUTURES EXCHANGE'], dtype=object)
```

## Release Shedule

The CFTC [releases](https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm) the reports every Friday at 3:30pm Eastern Time.
