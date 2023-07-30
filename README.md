# Weather Data Crawler

Download weather data from weather bureau.

## CWB, Central Weather Bureau of Taiwan

Crawl data from [Observation Data Inquire System](https://e-service.cwb.gov.tw/HistoryDataQuery/).

### Usage

Clone this repository, and run the following command in the terminal.

```bash
python get_cwb_observation.py --path <path> --start <start> --end <end>
```

The program will first crawl the station list from the website, and then crawl the data of each station.

### Parameters

| Parameter | Description           | Default        |
| --------- | --------------------- | -------------- |
| `--path`  | Path to save the data | `.`            |
| `--start` | Start date            | today - 7 days |
| `--end`   | End date              | today          |
