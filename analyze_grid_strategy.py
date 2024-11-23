import argparse
import os
import pandas as pd
from kline_downloader import run_download
from grid_strategy import analyze_grid_strategy

def main():
    parser = argparse.ArgumentParser(description='分析K线数据是否适合使用网格策略')
    parser.add_argument('--symbol', '-s', type=str, required=True, help='交易对符号，例如 "ETH" 或 "ETH/USDT"')
    parser.add_argument('--interval', '-i', type=str, default='15m', help='K线时间间隔，例如 "15m"')
    parser.add_argument('--start', '-st', type=str, help='开始日期，格式 "YYYY-MM-DD"')
    parser.add_argument('--end', '-ed', type=str, help='结束日期，格式 "YYYY-MM-DD"')
    parser.add_argument('--days', '-d', type=int, help='爬取最近多少天的数据')
    parser.add_argument('--save_to', '-o', type=str, default=None, help='保存的文件路径')
    parser.add_argument('--threshold_factor', '-t', type=float, default=1.0, help='判断网格策略适用性的阈值因子（相对标准差比例）。默认值为1.0')
    parser.add_argument('--in_memory', '-m', action='store_true', help='是否在内存中分析数据而不保存文件')
    parser.add_argument('--grid_step_percentage', '-g', type=float, default=1.0, help='推荐的网格步长百分比。默认值为1.0%')
    parser.add_argument('--max_grids', '-x', type=int, default=99, help='推荐的最大网格数量。默认值为99格')
    parser.add_argument('--atr_std_multiplier', '-a', type=float, default=1.0, help='ATR 阈值设定的标准差倍数。默认值为1.0')
    args = parser.parse_args()

    # 下载数据
    try:
        if args.in_memory:
            df = run_download(
                symbol=args.symbol,
                interval=args.interval,
                start=args.start,
                end=args.end,
                days=args.days,
                save_to=args.save_to,
                return_df=True
            )
            csv_path = None  # 不保存文件
        else:
            csv_path = run_download(
                symbol=args.symbol,
                interval=args.interval,
                start=args.start,
                end=args.end,
                days=args.days,
                save_to=args.save_to,
                return_df=False
            )
    except ValueError as ve:
        print(f"参数错误: {ve}")
        return
    except Exception as e:
        print(f"下载数据时发生错误: {e}")
        return

    # 分析数据
    if args.in_memory:
        if df is not None:
            is_suitable = analyze_grid_strategy(
                df=df,
                visualize=False,  # 关闭可视化
                threshold_factor=args.threshold_factor,
                grid_step_percentage=args.grid_step_percentage,
                max_grids=args.max_grids,
                atr_period=14,  # 使用默认ATR周期
                atr_std_multiplier=args.atr_std_multiplier,
                streamlit_mode=False
            )
        else:
            print("未能获取数据进行分析。")
            return
    else:
        if csv_path and os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                is_suitable = analyze_grid_strategy(
                    df=df,
                    visualize=False,  # 关闭可视化
                    threshold_factor=args.threshold_factor,
                    grid_step_percentage=args.grid_step_percentage,
                    max_grids=args.max_grids,
                    atr_period=14,  # 使用默认ATR周期
                    atr_std_multiplier=args.atr_std_multiplier,
                    streamlit_mode=False
                )
            except Exception as e:
                print(f"读取CSV文件时发生错误: {e}")
                return
        else:
            print(f"CSV文件不存在: {csv_path}")
            return

    if is_suitable:
        print("可以考虑使用网格策略进行交易。")
    else:
        print("不建议使用网格策略。")

if __name__ == '__main__':
    main()