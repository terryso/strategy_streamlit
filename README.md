
# Binance K-Line Data Analysis with Grid Strategy and Streamlit

## 项目简介

本项目旨在下载币安现货市场的历史K线数据，并使用网格策略对数据进行分析。通过命令行界面（CLI）和交互式Web应用（Streamlit）两种方式，用户可以轻松获取、分析和可视化交易数据，以辅助制定交易策略。

## 主要功能

- **下载币安现货历史K线数据**：获取任意交易对的历史K线数据，并保存至本地。
- **网格策略分析**：分析K线数据是否适合应用网格策略，并推荐网格价格范围和数量。
- **交互式可视化**：通过Streamlit应用，直观展示分析结果和相关图表。
- **命令行接口**：通过CLI进行数据下载和分析，适用于自动化脚本和批处理任务。

## 安装指南

### 环境要求

- Python 3.7及以上版本
- pip 包管理器

### 克隆仓库

```bash
git clone https://github.com/yourusername/binance_kline.git
cd binance_kline
```

### 创建虚拟环境（推荐）

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate    # Windows
```

### 安装依赖

```bash
pip install -r requirements.txt
```

## 使用指南

### 1. 下载币安现货历史K线数据

首先，您可以使用提供的函数下载特定交易对的K线数据。

#### 获取所有支持的交易对

```python
from grid_strategy import get_support_symbols

symbols = get_support_symbols()
print(symbols)
```

#### 下载数据至本地（默认下载OHLCV数据）

```python
from grid_strategy import download_full_klines

download_full_klines(
    symbol="BTC/USDT",
    interval="15m",
    start="2021-07-01",
    end="2021-08-01",
    save_to="path_to_file.csv"
)
```

### 2. 使用命令行接口（CLI）进行网格策略分析

CLI脚本 

analyze_grid_strategy.py

 允许您在命令行中执行网格策略分析。

#### 基本用法

```bash
python analyze_grid_strategy.py --symbol "ETH/USDT" --interval "1h" --start "2021-01-01" --end "2021-02-01"
```

#### 可用参数

- `--symbol` 或 `-s`：交易对符号，例如 `"ETH"` 或 `"ETH/USDT"`（必填）。
- `--interval` 或 `-i`：K线时间间隔，例如 `"15m"`、`"1h"`、`"1d"`；默认值为 `"15m"`。
- `--start` 或 `-st`：开始日期，格式 `"YYYY-MM-DD"`。
- `--end` 或 `-ed`：结束日期，格式 `"YYYY-MM-DD"`。
- `--days` 或 `-d`：爬取最近多少天的数据。
- `--save_to` 或 `-o`：保存的文件路径。
- `--threshold_factor` 或 `-t`：判断网格策略适用性的阈值因子（相对标准差比例）；默认值为 `1.0`。
- `--in_memory` 或 `-m`：是否在内存中分析数据而不保存文件。
- `--grid_step_percentage` 或 `-g`：推荐的网格步长百分比；默认值为 `1.0%`。
- `--max_grids` 或 `-x`：推荐的最大网格数量；默认值为 `99`。
- `--atr_std_multiplier` 或 `-a`：ATR 阈值设定的标准差倍数；默认值为 `1.0`。

#### 示例

```bash
python analyze_grid_strategy.py \
    --symbol "BTC/USDT" \
    --interval "30m" \
    --start "2021-07-01" \
    --end "2021-08-01" \
    --save_to "btc_usdt_20210701_20210801.csv" \
    --threshold_factor 1.5 \
    --grid_step_percentage 0.5 \
    --max_grids 50
```

### 3. 使用Streamlit应用进行交互式分析和可视化

Streamlit应用 

analyze_grid_strategy_streamlit.py

 提供了一个用户友好的Web界面，方便进行数据分析和结果可视化。

#### 运行Streamlit应用

```bash
streamlit run analyze_grid_strategy_streamlit.py
```

#### 应用功能和参数说明

启动应用后，您将在浏览器中看到以下功能和参数选项：

##### 3.1. 输入参数设置（位于侧边栏）

- **交易对符号 (symbol)**  
  输入您想要分析的交易对，例如 `"ETH"` 或 `"ETH/USDT"`。

- **K线时间间隔 (interval)**  
  选择K线的时间间隔，包括 `"1m"`、`"5m"`、`"15m"`、`"30m"`、`"1h"`、`"4h"`、`"1d"`。默认值为 `"15m"`。

- **选择日期范围**  
  - **最近多少天**：输入您想要下载的最近多少天的数据，例如 `30` 天。
  - **指定开始和结束日期**：选择具体的开始和结束日期，例如从 `2021-07-01` 到 `2021-08-01`。

- **保存的文件路径 (save_to)**  
  可选项，输入您希望将下载的数据保存到本地的文件路径，例如 `data/btc_usdt.csv`。

- **是否生成图表 (visualize)**  
  勾选此项以生成可视化图表，取消勾选则仅输出分析结果。

- **阈值因子 (threshold_factor)**  
  使用滑块选择判断网格策略适用性的阈值因子（相对标准差比例），范围 `0.1` 到 `3.0`，默认值为 `1.0`。

- **是否在内存中分析数据而不保存文件 (in_memory)**  
  勾选此项将在内存中进行数据分析，而不保存下载的文件。

- **推荐的网格步长百分比 (grid_step_percentage)**  
  滑块选择推荐的网格步长百分比，范围 `0.1%` 到 `5.0%`，默认值为 `1.0%`。

- **推荐的最大网格数量 (max_grids)**  
  输入推荐的最大网格数量，范围 `1` 到 `100`，默认值为 `99`。

- **ATR 阈值设定的标准差倍数 (atr_std_multiplier)**  
  使用滑块选择ATR阈值设定的标准差倍数，范围 `0.1` 到 `3.0`，默认值为 `1.0`。

##### 3.2. 运行分析

点击 **“运行分析”** 按钮，应用将开始下载和分析数据。完成后，您将看到以下内容：

- **分析结果**  
  显示是否适合使用网格策略，以及相关的统计信息。

- **推荐的网格价格范围和数量**  
  如果数据适合网格策略，应用将推荐网格的价格范围、数量和间隔。

- **图表展示**  
  - **收盘价走势图**  
    显示所选交易对在指定日期范围内的收盘价变化。
  
  - **价格波动范围与ATR**  
    展示价格波动范围和ATR（平均真实波动幅度）的变化。

- **网格价格级别表格**  
  列出推荐的各格价格级别，便于参考和实施。

##### 3.3. 交互式特性

- **实时图表更新**  
  根据输入参数的不同，图表将实时更新，帮助您更直观地理解数据。
  
- **信息通知**  
  使用不同颜色的通知框（如错误、警告、信息、成功）提示分析过程中的重要信息和结果。

- **气球动画**  
  分析适用网格策略后，应用会显示气球动画以表示成功。

## 项目结构

```
binance_kline/
├── analyze_grid_strategy.py           # CLI脚本，用于网格策略分析
├── analyze_grid_strategy_streamlit.py # Streamlit应用脚本
├── grid_strategy.py                   # 核心分析逻辑
├── kline_downloader.py                # K线数据下载功能
├── requirements.txt                   # 项目依赖
├── README.md                          # 项目文档
└── data/                              # 存储下载的数据文件
```

## 依赖库

项目所需的Python库已列在 

requirements.txt

 文件中。主要依赖包括：

- **streamlit**：用于构建交互式Web应用。
- **pandas**：进行数据处理和分析。
- **altair**：创建声明式统计可视化。
- **numpy**：支持高性能的数值计算。

### 安装依赖

```bash
pip install -r requirements.txt
```

## 常见问题

### 图表无法显示

- **解决方法**：确保已正确安装所有依赖库，特别是 `altair`。可以使用以下命令重新安装：
  
  ```bash
  pip install --upgrade altair
  ```

### 数据下载失败

- **解决方法**：
  - 检查网络连接是否正常。
  - 确认输入的交易对符号和时间间隔是否正确。
  - 确保指定的保存路径具有写入权限。

### 运行应用时报错

- **解决方法**：
  - 检查Python版本是否符合要求（3.7及以上）。
  - 确认所有依赖库已正确安装。
  - 阅读错误信息，针对性解决问题。

## 贡献指南

欢迎贡献代码和提出改进建议！请按照以下步骤进行：

1. **Fork 本仓库**  
   点击右上角的 "Fork" 按钮，将仓库复制到您的账户。

2. **创建新分支**  
   ```bash
   git checkout -b feature/新功能名称
   ```

3. **提交更改**  
   ```bash
   git commit -m "添加了新功能"
   ```

4. **推送到分支**  
   ```bash
   git push origin feature/新功能名称
   ```

5. **创建Pull Request**  
   在GitHub上提交Pull Request，描述您的更改和改进。

## 许可协议

本项目采用 MIT 许可证 许可。详情请参阅 LICENSE 文件。

## 联系方式

如有任何问题或建议，请通过 [GitHub Issues](https://github.com/terryso/strategy_streamlit/issues) 联系我们。
