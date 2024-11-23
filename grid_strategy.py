import pandas as pd

def analyze_grid_strategy(df, visualize=True, threshold_factor=1.0, grid_step_percentage=1.0,
                         max_grids=10, atr_period=14, atr_std_multiplier=1.0, streamlit_mode=False):
    """
    分析K线数据是否适合使用网格策略，并推荐网格价格范围和网格数量。
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

    if streamlit_mode and visualize:
        plot_price_atr = {
            'title': f'价格波动范围与ATR({atr_period})',
            'x': df['open_time'],
            'y': df[['price_change', 'ATR']],
            'xlabel': '时间',
            'ylabel': '值 (USDT)',
            'labels': ['价格波动范围', f'ATR({atr_period})']
        }
        output.append(('plot', plot_price_atr))

    # 自动计算 min_atr 和 max_atr 基于均值和标准差
    atr_mean = df['ATR'].mean()
    atr_std = df['ATR'].std()
    min_atr = atr_mean - atr_std_multiplier * atr_std
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

        # 推荐网格价格范围
        min_price = df['close'].min()
        max_price = df['close'].max()
        price_range = max_price - min_price
        message = f"推荐的网格价格范围: {min_price:.2f} USDT - {max_price:.2f} USDT"
        if streamlit_mode:
            output.append(('info', message))
        else:
            print(message)

        # 推荐网格数量
        recommended_grids = min(int(price_range / (min_price * grid_step_percentage / 100)), max_grids)
        recommended_grids = recommended_grids if recommended_grids > 0 else 1
        message = f"推荐的网格数量: {recommended_grids}"
        if streamlit_mode:
            output.append(('info', message))
        else:
            print(message)

        # 计算网格间隔
        grid_interval = price_range / recommended_grids
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