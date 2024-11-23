import pandas as pd

def analyze_grid_strategy(df, visualize=True, threshold_factor=1.0, grid_step_percentage=1.0,
                         max_grids=10, atr_period=14, atr_std_multiplier=2.0, macd_fast=12, macd_slow=26, macd_signal=9,
                         streamlit_mode=False):
    """
    分析K线数据是否适合使用网格策略，并推荐网格价格范围和网格数量。
    集成MACD指标以预测未来价格范围。
    """
    output = []

    # 检查必要的列是否存在
    required_columns = {"open_time", "high", "low", "close"}
    if not required_columns.issubset(df.columns):
        message = f"DataFrame缺少必要的列: {required_columns}"
        if streamlit_mode:
            output.append(('error', message))
        else:
            print(message)
        return False

    # 转换时间格式
    df['open_time'] = pd.to_datetime(df['open_time'])

    if streamlit_mode and visualize:
        plot_close_price = {
            'title': '收盘价走势图',
            'x': df['open_time'],
            'y': df['close'],
            'xlabel': '时间',
            'ylabel': '价格 (USDT)',
            'labels': ['收盘价']
        }
        output.append(('plot', plot_close_price))

    # 计算价格波动范围
    df['price_change'] = df['high'] - df['low']
    average_change = df['price_change'].mean()
    std_dev_change = df['price_change'].std()
    message = f'平均价格波动范围: {average_change:.2f} USDT\n价格波动标准差: {std_dev_change:.2f} USDT'
    if streamlit_mode:
        output.append(('info', message))
    else:
        print(message)

    # 计算ATR（平均真实波动幅度）
    df['H-L'] = df['high'] - df['low']
    df['H-PC'] = abs(df['high'] - df['close'].shift(1))
    df['L-PC'] = abs(df['low'] - df['close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    df['ATR'] = df['TR'].rolling(window=atr_period).mean()
    latest_atr = df['ATR'].iloc[-1]
    message = f'最新ATR（{atr_period}期）: {latest_atr:.2f} USDT'
    if streamlit_mode:
        output.append(('info', message))
    else:
        print(message)

    # 计算MACD指标
    df['EMA_fast'] = df['close'].ewm(span=macd_fast, adjust=False).mean()
    df['EMA_slow'] = df['close'].ewm(span=macd_slow, adjust=False).mean()
    df['MACD'] = df['EMA_fast'] - df['EMA_slow']
    df['MACD_signal'] = df['MACD'].ewm(span=macd_signal, adjust=False).mean()
    df['MACD_hist'] = df['MACD'] - df['MACD_signal']
    latest_macd = df['MACD'].iloc[-1]
    latest_macd_signal = df['MACD_signal'].iloc[-1]
    latest_macd_hist = df['MACD_hist'].iloc[-1]

    message = f'最新MACD: {latest_macd:.2f}\n最新信号线: {latest_macd_signal:.2f}\n最新柱状图: {latest_macd_hist:.2f}'
    if streamlit_mode:
        output.append(('info', message))
    else:
        print(message)

    if streamlit_mode and visualize:
        plot_macd = {
            'title': 'MACD指标',
            'x': df['open_time'],
            'y': df[['MACD', 'MACD_signal', 'MACD_hist']],
            'xlabel': '时间',
            'ylabel': '值',
            'labels': ['MACD', '信号线', '柱状图']
        }
        output.append(('plot', plot_macd))

    # 自动计算 min_atr 和 max_atr 基于均值和标准差
    atr_mean = df['ATR'].mean()
    atr_std = df['ATR'].std()
    min_atr = max(0, atr_mean - atr_std_multiplier * atr_std)  # 确保 min_atr 不小于零
    max_atr = atr_mean + atr_std_multiplier * atr_std
    message = f'自动设定最低ATR阈值 (mean - {atr_std_multiplier}*std): {min_atr:.2f} USDT\n' \
              f'自动设定最高ATR阈值 (mean + {atr_std_multiplier}*std): {max_atr:.2f} USDT'
    if streamlit_mode:
        output.append(('info', message))
    else:
        print(message)

    # 使用相对标准差和 ATR 作为阈值
    relative_std = std_dev_change / average_change if average_change != 0 else float('inf')
    message = f'相对标准差: {relative_std:.2f}\n最新ATR: {latest_atr:.2f} USDT\n阈值因子 (threshold_factor): {threshold_factor}\n' \
              f'最低ATR阈值 (min_atr): {min_atr:.2f} USDT\n最高ATR阈值 (max_atr): {max_atr:.2f} USDT'
    if streamlit_mode:
        output.append(('info', message))
    else:
        print(message)

    # 判断是否适合网格策略
    suitable = (relative_std <= threshold_factor) and (latest_atr >= min_atr) and (latest_atr <= max_atr)
    if suitable:
        if streamlit_mode:
            output.append(('success', "数据适合使用网格策略。"))
        else:
            print("数据适合使用网格策略。")

        # 推荐网格价格范围基于MACD趋势
        current_price = df['close'].iloc[-1]
        if latest_macd > latest_macd_signal:
            # MACD在上升趋势，设置最大价格增加50%，最小价格减少20%
            max_price = current_price * 1.3
            min_price = current_price * 0.85
            message = "MACD显示上升趋势，适合做多。"
        else:
            # MACD在下降趋势，设置最大价格减少20%，最小价格增加50%
            max_price = current_price * 1.15
            min_price = current_price * 0.7
            message = "MACD显示下降趋势，适合做空。"

        if streamlit_mode:
            output.append(('info', message))
        else:
            print(message)

        message = f"推荐的网格价格范围: {min_price:.2f} USDT - {max_price:.2f} USDT"
        if streamlit_mode:
            output.append(('info', message))
        else:
            print(message)

        # 推荐网格数量
        grid_step = current_price * grid_step_percentage / 100
        recommended_grids = min(int((max_price - min_price) / grid_step), max_grids)
        recommended_grids = recommended_grids if recommended_grids > 0 else 1
        message = f"推荐的网格数量: {recommended_grids}"
        if streamlit_mode:
            output.append(('info', message))
        else:
            print(message)

        # 计算网格间隔
        grid_interval = (max_price - min_price) / recommended_grids
        message = f"推荐的网格间隔: {grid_interval:.2f} USDT"
        if streamlit_mode:
            output.append(('info', message))
        else:
            print(message)

        # 输出网格价格级别
        grid_prices = [min_price + i * grid_interval for i in range(recommended_grids + 1)]
        message = "推荐的网格价格级别:"
        if streamlit_mode:
            grid_levels = {f"格 {idx}": f"{price:.2f} USDT" for idx, price in enumerate(grid_prices)}
            output.append(('table', pd.DataFrame.from_dict(grid_levels, orient='index', columns=['价格'])))
        else:
            print(message)
            for idx, price in enumerate(grid_prices):
                print(f"格 {idx}: {price:.2f} USDT")
    else:
        if streamlit_mode:
            output.append(('warning', "数据不适合使用网格策略。"))
        else:
            print("数据不适合使用网格策略。")

    if streamlit_mode:
        return suitable, output
    else:
        return suitable