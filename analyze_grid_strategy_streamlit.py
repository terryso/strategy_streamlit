import streamlit as st
import pandas as pd
from grid_strategy import analyze_grid_strategy
from kline_downloader import run_download
from datetime import datetime, timedelta
import os
import altair as alt  # 引入Altair用于高级图表

def main():
    st.title("网格策略分析工具")

    st.sidebar.header("输入参数")

    # 输入参数
    symbol = st.sidebar.text_input("交易对符号 (例如 ETH 或 ETH/USDT)", value="ETH/USDT")
    interval = st.sidebar.selectbox("K线时间间隔", options=["1m", "5m", "15m", "30m", "1h", "4h", "1d"], index=2)

    date_option = st.sidebar.radio("选择日期范围", ("最近多少天", "指定开始和结束日期"))

    if date_option == "最近多少天":
        days = st.sidebar.number_input("爬取最近多少天的数据", min_value=1, max_value=365, value=30, step=1)
        start = None
        end = None
    else:
        days = None
        start = st.sidebar.date_input("开始日期", value=datetime.now() - timedelta(days=30))
        end = st.sidebar.date_input("结束日期", value=datetime.now())
        if start and end:
            if start > end:
                st.sidebar.error("结束日期必须在开始日期之后。")
                st.stop()

    save_to = st.sidebar.text_input("保存的文件路径 (可选)", value=None)
    visualize = st.sidebar.checkbox("是否生成图表", value=True)
    threshold_factor = st.sidebar.slider("阈值因子 (threshold_factor)", min_value=0.1, max_value=3.0, value=1.0, step=0.1)
    in_memory = st.sidebar.checkbox("是否在内存中分析数据而不保存文件", value=True)
    grid_step_percentage = st.sidebar.slider("推荐的网格步长百分比", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
    max_grids = st.sidebar.number_input("推荐的最大网格数量", min_value=1, max_value=100, value=99, step=1)
    atr_std_multiplier = st.sidebar.slider("ATR 阈值设定的标准差倍数", min_value=0.1, max_value=3.0, value=1.0, step=0.1)

    if st.sidebar.button("运行分析"):
        with st.spinner("下载和分析数据..."):
            try:
                df = run_download(
                    symbol=symbol,
                    interval=interval,
                    start=start.strftime("%Y-%m-%d") if start else None,
                    end=end.strftime("%Y-%m-%d") if end else None,
                    days=days,
                    save_to=save_to,
                    return_df=True if in_memory else False
                )

                if not in_memory and save_to:
                    if os.path.exists(save_to):
                        st.success(f"数据已保存至: {save_to}")
                    else:
                        st.error("数据下载失败或文件未保存。")

                if df is not None:
                    is_suitable, analysis_output = analyze_grid_strategy(
                        df=df,
                        visualize=visualize,
                        threshold_factor=threshold_factor,
                        grid_step_percentage=grid_step_percentage,
                        max_grids=max_grids,
                        atr_period=14,  # 使用默认ATR周期
                        atr_std_multiplier=atr_std_multiplier,
                        streamlit_mode=True
                    )

                    # 处理分析输出
                    for item in analysis_output:
                        if item[0] == 'error':
                            st.error(item[1])
                        elif item[0] == 'info':
                            st.info(item[1])
                        elif item[0] == 'warning':
                            st.warning(item[1])
                        elif item[0] == 'success':
                            st.success(item[1])
                        elif item[0] == 'plot':
                            plot_details = item[1]
                            title = plot_details['title']
                            x = plot_details['x']
                            y = plot_details['y']
                            xlabel = plot_details['xlabel']
                            ylabel = plot_details['ylabel']
                            labels = plot_details['labels']

                            # 移除调试信息
                            # st.write(f"绘图标题: {title}")
                            # st.write("X 数据:", x)
                            # st.write("Y 数据:", y)

                            if isinstance(y, pd.DataFrame):
                                # 多指标图表，使用 Altair
                                chart_data = y.copy()
                                chart_data['时间'] = x
                                chart_data = chart_data.melt('时间', var_name='指标', value_name='值')

                                chart = alt.Chart(chart_data).mark_line().encode(
                                    x='时间:T',
                                    y='值:Q',
                                    color='指标:N'
                                ).properties(
                                    title=title
                                )

                                st.altair_chart(chart, use_container_width=True)
                            elif isinstance(y, pd.Series):
                                # 单一指标，使用 st.line_chart
                                y_df = pd.DataFrame({labels[0]: y.values}, index=x)
                                st.line_chart(y_df)
                            else:
                                # 其他类型，使用 st.line_chart
                                st.line_chart(pd.DataFrame({'值': y}, index=x))

                        elif item[0] == 'table':
                            st.table(item[1])

                    if is_suitable:
                        st.balloons()
                else:
                    st.error("未能获取数据进行分析。")
            except ValueError as ve:
                st.error(f"参数错误: {ve}")
            except Exception as e:
                st.error(f"发生错误: {e}")

if __name__ == '__main__':
    main()