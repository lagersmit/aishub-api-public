# aishub_api
Retrieves AISrecords from aishub and can store the result in a pandas dataframe.
All compression methods (none, zip, gzip, bzip2) are supported.
Also xml, json and csv output is supported. The aishub_api.parse_message function can convert any valid api message into a header plus dataframe.

## About
Python script to retrieve records using the AISHub API.

## Prerequisites
Software: Python 3.8.5+

Modules: Pandas, requests

## Usage
### Example I
```
import aishub_api

aishub_username = "your_username"

config = aishub_api.AISHubApiConfig(aishub_username)
retrieved_message = aishub_api.retrieve_vessel_record(cfg, mmsi=244660616)
parsed_msg = aishub_api.parse_message(query_result)
print(parsed_msg.content.to_markdown())
```
|    |      MMSI | TIME                    |   LONGITUDE |   LATITUDE |   COG |   SOG |   HEADING |   ROT |   NAVSTAT |   IMO | NAME      | CALLSIGN   |   TYPE |   A |   B |   C |   D |   DRAUGHT | DEST   | ETA         |
|---:|----------:|:------------------------|------------:|-----------:|------:|------:|----------:|------:|----------:|------:|:----------|:-----------|-------:|----:|----:|----:|----:|----------:|:-------|:------------|
|  0 | 244660616 | 2020-08-17 12:36:27 GMT |     6.17468 |    51.8392 |   360 |     0 |       121 |     0 |         0 |     0 | EDELWEISS | PE6813     |     89 |  86 |   0 |  13 |   0 |       0.2 | SPYCK  | 00-00 00:00 |

### Example II
```
import aishub_api

aishub_username = "your_username"

config = aishub_api.AISHubApiConfig(aishub_username,
                                     output=aishub_api.Output.XML,
                                     compress=aishub_api.Compress.BZIP2)
retrieved_message = aishub_api.retrieve_vessel_records(cfg)
parsed_msg = aishub_api.parse_message(query_result, 
                                      output=aishub_api.Output.XML)
print(parsed_msg.content.to_markdown())
```
|    |      MMSI | TIME                    |   LONGITUDE |   LATITUDE |   COG |   SOG |   HEADING |   ROT |   NAVSTAT |     IMO | NAME                | CALLSIGN   |   TYPE |   A |   B |   C |   D |   DRAUGHT | DEST           | ETA         |
|---:|----------:|:------------------------|------------:|-----------:|------:|------:|----------:|------:|----------:|--------:|:--------------------|:-----------|-------:|----:|----:|----:|----:|----------:|:---------------|:------------|
|  0 | 244620862 | 2020-08-17 12:42:16 GMT |     5.2867  |    52.6986 | 166.5 |     0 |       511 |   128 |        15 |       0 | WHITE WITCH IN BLUE | PH7043     |     36 |   9 |   4 |   1 |   3 |       0   |                | 00-00 24:60 |
|  1 | 257308600 | 2020-08-17 12:42:57 GMT |    10.9921  |    64.9582 | 307.4 |     0 |        56 |     0 |         0 | 7017600 | HARANES             | LGSN       |     69 |  13 |  15 |   4 |   4 |       2.7 | W              | 08-14 22:30 |
|  2 | 338142177 | 2020-08-17 12:38:44 GMT |  -123.173   |    48.6037 |  14.5 |     0 |       511 |   128 |        15 |       0 | PLANE CRAZY         |            |     37 |   7 |   8 |   2 |   3 |       0   |                | 00-00 00:00 |
|  3 | 211626290 | 2020-08-17 12:43:16 GMT |     8.21039 |    53.1247 |   0   |     0 |       216 |     0 |         0 |       0 | DRIELAKE            | DF8347     |     33 |  14 |   5 |   1 |   4 |       0.2 |                | 01-01 00:00 |
|  4 | 244700554 | 2020-08-17 12:38:19 GMT |     4.40764 |    51.2288 | 360   |     0 |       511 |   128 |         5 |       0 | MALECON             | PB7981     |     37 |  14 |   6 |   3 |   3 |      16   | WILLEMDOK ANTW | 08-16 16:30 |

## License
Distributed under the GNU GPLv3 License. See LICENSE for more information.

## Contact
email: ferdi.stoeltie@lagersmit.com
