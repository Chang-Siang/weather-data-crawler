# %%
import os
import argparse
import urllib
import datetime
import numpy as np
import pandas as pd

# %%
parser = argparse.ArgumentParser(description='Get Central Weather Bureau Observation Data', usage='python get_cwb_observation.py --path <path> --start <start> --end <end>')
parser.add_argument('--path', type=str, default=os.path.dirname(os.path.abspath('__file__')), help='path to save data', required=False, dest='path')
parser.add_argument('--start', type=str, default=(datetime.date.today()-datetime.timedelta(days=7)).strftime('%Y-%m-%d'), help='YYYY-MM-DD', required=False, dest='start')
parser.add_argument('--end', type=str, default=datetime.date.today().strftime('%Y-%m-%d'), help='YYYY-MM-DD', required=False, dest='end')
args = parser.parse_args()

# %%
BATH_PATH = args.path

ETC_PATH = os.path.join(BATH_PATH, "data/central-weather-bureau-observation")

START = datetime.datetime.strptime(args.start, '%Y-%m-%d').date()

END = datetime.datetime.strptime(args.end, '%Y-%m-%d').date()
# %%

if not os.path.exists(ETC_PATH):
    os.makedirs(ETC_PATH)

# %% [markdown]
# ## Meta
# 
# Read webpage and get meta data.
# 

# %%
def get_meta_of_stations():
    link = "https://e-service.cwb.gov.tw/wdps/obs/state.htm"
    response = pd.read_html(link)[0] # 0: 現存測站, 1: 已撤銷測站, 2: 暫停供應資料測站

    # Extract columns of station number, station id, altitude (meter), city, lontitude, latitude, and station address
    meta = response.loc[:, ["站號", "站名", "海拔高度(m)", "城市", "經度", "緯度", "地址", "資料起始日期"]]
    meta = meta.rename(columns={
        "站號": "StationID", "站名": "StationName", "海拔高度(m)": "Altitude", 
        "城市": "City", "經度": "Lon", "緯度": "Lat", "地址": "Address", 
        "資料起始日期": "StartDate"
    })
    return meta

# %%
meta = get_meta_of_stations()
meta.to_json(os.path.join(ETC_PATH, "meta.json"), orient='records', force_ascii=False)

# %% [markdown]
# ## Download
# 

# %%
def get_weather_data(stn, st_name, date, altitude):
    st_name = urllib.parse.quote(urllib.parse.quote(st_name))
    url = f"https://e-service.cwb.gov.tw/HistoryDataQuery/DayDataController.do?command=viewMain&station={stn}&stname={st_name}&datepicker={date}&altitude={altitude}"
    data = pd.read_html(url, encoding='utf-8')[1] # 0: Page Title, 1: Data Content
    data.columns = [i[2] for i in np.array(data.columns)] # 0: Short Name, 1: Long Name(tw), 2: Long Name(en) 
    data.insert(loc=0, column="Date", value=date)
    return data

# %%
# Read the meta data 
meta = pd.read_json(os.path.join(ETC_PATH, "meta.json"))

# Only keep the ground weather stations(^46) and the start date is after then START
meta = meta[meta['StationID'].str.contains("^46")].reset_index(drop=True)
meta = meta[pd.to_datetime(meta['StartDate']) <= pd.to_datetime(START)].reset_index(drop=True)

# %%
# According to the list of stations to access to data
for i, row in meta.iterrows():
    delta = pd.date_range(start=START, end=END).tolist()
    data = pd.concat([get_weather_data(row["StationID"], row["StationName"], str(date.date()), row["Altitude"]) for date in delta]) \
        .sort_values(['Date', 'ObsTime']) \
        .reset_index(drop=True)
    data.insert(loc=1, column="Station", value=row["StationID"])
    data.insert(loc=1, column="Lat", value=row["Lat"])
    data.insert(loc=1, column="Lon", value=row["Lon"])
    data.insert(loc=1, column="City", value=row["City"])
    data.to_csv(os.path.join(ETC_PATH, F'{row["StationID"]}.csv'), index=False)
