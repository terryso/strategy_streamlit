
import time
import requests
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from tqdm import tqdm
import argparse
import os  # 添加导入

BASE_URL = "https://api.binance.com" if os.getenv("RUN_ENV") == "local" else "https://api.binance.us"
REQ_LIMIT = 1000
SUPPORT_INTERVAL = {"1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"}

def get_support_symbols():
    res = []
    end_point = "/api/v3/exchangeInfo"
    resp = requests.get(BASE_URL + end_point)
    for symbol_info in resp.json()["symbols"]:
        if symbol_info["status"] == "TRADING":
            symbol = "{}/{}".format(symbol_info["baseAsset"].upper(), symbol_info["quoteAsset"].upper())
            res.append(symbol)
    return res

def get_klines(symbol, interval='1h', since=None, limit=1000, to=None):
    end_point = "/api/v3/klines"
    params = {
        'symbol': symbol,
        'interval': interval,
        'startTime': since * 1000 if since else None,
        'limit': limit,
        'endTime': to * 1000 if to else None
    }
    resp = requests.get(BASE_URL + end_point, params=params)
    return resp.json()

def download_full_klines(symbol, interval, start, end=None, save_to=None, req_interval=None, dimension="ohlcv", return_df=False):
    if interval not in SUPPORT_INTERVAL:
        raise Exception("interval {} is not support!!!".format(interval))
    start_end_pairs = get_start_end_pairs(start, end, interval)
    klines = []
    for (start_ts, end_ts) in tqdm(start_end_pairs):
        tmp_kline = get_klines(symbol.replace("/", ""), interval, since=start_ts, limit=REQ_LIMIT, to=end_ts)
        if len(tmp_kline) > 0:
            klines.append(tmp_kline)
        if req_interval:
            time.sleep(req_interval)

    klines = np.concatenate(klines)
    data = []
    cols = ["open_time", "open", "high", "low", "close", "volume",
            "close_time", "value", "trade_cnt",
            "active_buy_volume", "active_buy_value"]

    for i in range(len(klines)):
        tmp_kline = klines[i]
        data.append(tmp_kline[:-1])

    df = pd.DataFrame(np.array(data), columns=cols, dtype=float)
    df.drop("close_time", axis=1, inplace=True)
    for col in cols:
        if col in ["open_time", "trade_cnt"]:
            df[col] = df[col].astype(int)
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")

    if dimension == "ohlcv":
        df = df[cols[:6]]

    real_start = df["open_time"].iloc[0].strftime("%Y-%m-%d")
    real_end = df["open_time"].iloc[-1].strftime("%Y-%m-%d")

    if return_df:
        return df

    if save_to:
        df.to_csv(save_to, index=False)
    else:
        save_to = "{}_{}_{}_{}.csv".format(symbol.replace("/", "-"), interval, real_start, real_end)
        df.to_csv(save_to, index=False)
    
    return save_to  # 返回保存的文件路径

def get_start_end_pairs(start, end, interval):
    start_dt = datetime.strptime(start, "%Y-%m-%d")
    if end is None:
        end_dt = datetime.now()
    else:
        end_dt = datetime.strptime(end, "%Y-%m-%d")
    start_dt_ts = int(time.mktime(start_dt.timetuple()))
    end_dt_ts = int(time.mktime(end_dt.timetuple()))

    ts_interval = interval_to_seconds(interval)

    res = []
    cur_start = cur_end = start_dt_ts
    while cur_end < end_dt_ts - ts_interval:
        cur_end = min(end_dt_ts, cur_start + (REQ_LIMIT - 1) * ts_interval)
        res.append((cur_start, cur_end))
        cur_start = cur_end + ts_interval
    return res

def interval_to_seconds(interval):
    seconds_per_unit = {"m": 60, "h": 60 * 60, "d": 24 * 60 * 60, "w": 7 * 24 * 60 * 60}
    return int(interval[:-1]) * seconds_per_unit[interval[-1]]

def run_download(symbol, interval='15m', start=None, end=None, days=None, save_to=None, return_df=False):
    # 将 symbol 转换为大写
    symbol = symbol.upper()
    if '/' not in symbol:
        symbol = f"{symbol}/USDT"

    # 处理日期参数
    if days:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        start = start_date.strftime("%Y-%m-%d")
        end = end_date.strftime("%Y-%m-%d")
    else:
        if not start or not end:
            raise ValueError("当不使用 --days 时，必须提供 --start 和 --end")
    
    # 设置保存路径，包含 interval、start 和 end
    if not save_to and not return_df:
        save_to = f'{symbol.replace("/", "_")}_{interval}_{start}_{end}.csv'

    if return_df:
        # 直接返回 DataFrame 而不保存文件
        df = download_full_klines(symbol=symbol, interval=interval, start=start, end=end, save_to=save_to, return_df=True)
        return df

    # 检查文件是否已存在
    if os.path.exists(save_to):
        print(f"文件已存在: {save_to}，跳过下载。")
        return save_to

    # 调用下载函数
    download_full_klines(symbol=symbol, interval=interval, start=start, end=end, save_to=save_to)

    return save_to  # 返回保存的文件路径

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='下载K线数据')
    parser.add_argument('--symbol', type=str, required=True, help='交易对符号，例如 "ETH/USDT" 或 "ETH"')
    parser.add_argument('--interval', type=str, default='15m', help='K线时间间隔，例如 "15m"')
    parser.add_argument('--start', type=str, help='开始日期，格式 "YYYY-MM-DD"')
    parser.add_argument('--end', type=str, help='结束日期，格式 "YYYY-MM-DD"')
    parser.add_argument('--days', type=int, help='爬取最近多少天的数据')
    parser.add_argument('--save_to', type=str, default=None, help='保存的文件路径')
    args = parser.parse_args()

    save_to = run_download(
        symbol=args.symbol,
        interval=args.interval,
        start=args.start,
        end=args.end,
        days=args.days,
        save_to=args.save_to
    )
    
    # symbols = get_support_symbols()
    # usdt_symbols = []
    # for symbol in symbols:
    #     if 'usdt' in symbol.lower():
    #         usdt_symbols.append(symbol)
    #         # print(symbol)
    # print(f"支持的USDT交易对: {usdt_symbols}")
