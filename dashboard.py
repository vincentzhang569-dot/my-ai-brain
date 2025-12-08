import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os


# 页面配置 - 移动端优化
# st.set_page_config(
#     page_title="工业物联网预测性维护大屏",
#     layout="wide",
#     initial_sidebar_state="collapsed"  # 移动端默认收起侧边栏
# )

# 自定义 CSS 样式 - 工业中控室风格 + 移动端优化
st.markdown("""
<style>
    /* ========== 基础样式 ========== */
    .main {
        background-color: #0e1117;
    }
    .stApp {
        background-color: #0e1117;
    }
    
    /* ========== 标题样式 ========== */
    h1, h2, h3 {
        color: #ffffff;
        font-family: 'Arial', 'Microsoft YaHei', '微软雅黑', sans-serif;
        font-weight: bold;
        text-shadow: none;
    }
    
    /* 移动端标题优化 */
    @media (max-width: 768px) {
        h1 {
            font-size: 1.5rem !important;
            margin-bottom: 0.5rem !important;
        }
        h2 {
            font-size: 1.2rem !important;
            margin-bottom: 0.5rem !important;
        }
        h3 {
            font-size: 1rem !important;
        }
    }
    
    /* ========== 卡片样式 ========== */
    .metric-card {
        background: linear-gradient(135deg, #1a1f2e 0%, #252b3f 100%);
        border: 2px solid;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
        margin: 5px;
        transition: transform 0.2s ease;
    }
    
    /* 移动端卡片优化 */
    @media (max-width: 768px) {
        .metric-card {
            padding: 12px;
            margin: 3px;
            border-radius: 8px;
        }
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
    }
    
    .status-running {
        border-color: #00ff41;
        box-shadow: 0 0 20px rgba(0, 255, 65, 0.3);
    }
    .status-warning {
        border-color: #ffd700;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
    }
    .status-error {
        border-color: #ff0000;
        box-shadow: 0 0 20px rgba(255, 0, 0, 0.3);
    }
    
    .robot-name {
        font-size: 18px;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 8px;
    }
    
    @media (max-width: 768px) {
        .robot-name {
            font-size: 14px;
            margin-bottom: 5px;
        }
    }
    
    .status-text {
        font-size: 20px;
        font-weight: bold;
        margin: 10px 0;
    }
    
    @media (max-width: 768px) {
        .status-text {
            font-size: 16px;
            margin: 8px 0;
        }
    }
    
    .metric-value {
        font-size: 14px;
        color: #b0b0b0;
        margin: 3px 0;
    }
    
    @media (max-width: 768px) {
        .metric-value {
            font-size: 12px;
            margin: 2px 0;
        }
    }
    
    /* ========== 侧边栏优化 ========== */
    .sidebar .sidebar-content {
        background-color: #1a1f2e;
    }
    
    /* ========== 移动端布局优化 ========== */
    @media (max-width: 768px) {
        /* 主容器优化 */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
            padding-left: 0.5rem;
            padding-right: 0.5rem;
            max-width: 100%;
        }
        
        /* 列布局优化 - 移动端单列 */
        [data-testid="column"] {
            min-width: 100% !important;
            width: 100% !important;
            padding: 0.25rem !important;
            flex: 1 1 100% !important;
        }
        
        /* Streamlit 列容器优化 */
        .row-widget.stHorizontal {
            flex-direction: column !important;
        }
        
        /* Metric 组件优化 */
        [data-testid="stMetricValue"] {
            font-size: 1.5rem !important;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.9rem !important;
        }
        
        /* 表格优化 */
        .dataframe {
            font-size: 12px !important;
        }
        
        /* 按钮优化 */
        .stButton > button {
            width: 100%;
            font-size: 14px;
            padding: 0.5rem;
        }
        
        /* 图表容器优化 */
        .js-plotly-plot {
            width: 100% !important;
            height: auto !important;
        }
        
        /* 图表Y轴标签优化 - 确保水平显示 */
        .ytitle {
            writing-mode: horizontal-tb !important;
            text-orientation: mixed !important;
            transform: none !important;
        }
        
        /* Plotly Y轴标题强制水平 */
        .g-ytitle {
            text-orientation: mixed !important;
            writing-mode: horizontal-tb !important;
            transform: none !important;
        }
        
        /* Plotly Y轴标题文本 */
        .g-ytitle text {
            text-anchor: middle !important;
            dominant-baseline: middle !important;
        }
        
        /* 图表间距优化 */
        .plotly {
            margin-bottom: 20px !important;
        }
        
        /* 子图标题优化 */
        .g-xtitle, .g-ytitle {
            font-size: 11px !important;
        }
        
        /* Plotly图表容器响应式 */
        .plotly-graph-div {
            width: 100% !important;
            max-width: 100% !important;
        }
    }
    
    /* ========== 性能优化 ========== */
    /* 减少重绘 */
    * {
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    /* 优化滚动 */
    * {
        scroll-behavior: smooth;
    }
    
    /* 隐藏 Streamlit 默认元素（移动端） */
    @media (max-width: 768px) {
        #MainMenu {
            visibility: hidden;
        }
        footer {
            visibility: hidden;
        }
        header {
            visibility: hidden;
        }
        
        /* 触摸优化 */
        * {
            -webkit-tap-highlight-color: rgba(0, 212, 255, 0.2);
            touch-action: manipulation;
        }
        
        /* 优化表格滚动 */
        .dataframe {
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }
        
        /* 优化侧边栏 */
        [data-testid="stSidebar"] {
            width: 100% !important;
        }
        
        /* 优化图表响应式 */
        .plotly {
            width: 100% !important;
            height: auto !important;
        }
    }
    
    /* ========== 通用性能优化 ========== */
    /* 减少动画（低性能设备） */
    @media (prefers-reduced-motion: reduce) {
        * {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- 🚀 优化开始：使用 cache_data 缓存数据读取 ---
# ttl=600 表示缓存 600秒(10分钟)后过期，自动刷新一次，保证数据不过于陈旧
@st.cache_data(ttl=600) 
def load_data():
    # 这里放原本的读取逻辑
    if not os.path.exists("robot_sensor_data.csv"):
        # ... (你之前的生成代码) ...
        from generate_data import generate_robot_data
        generate_robot_data()
    
    df = pd.read_csv("robot_sensor_data.csv")
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    return df

# 使用缓存函数加载数据
df = load_data()
# --- 🚀 优化结束 ---

# 加载数据
try:
    # 显示加载状态（仅在首次加载时）
    if 'data_loaded' not in st.session_state:
        with st.spinner('🔄 正在加载数据...'):
            st.session_state.data_loaded = True
    
    # 页面标题
    st.markdown("<h1 style='text-align: center;'>🏭 工业物联网预测性维护大屏</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #888;'>Industrial IoT Predictive Maintenance Dashboard</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    # ============ 1. 全局概览 - 状态卡片 ============
    st.markdown("<h2>📊 实时状态监控</h2>", unsafe_allow_html=True)
    
    # 获取每台机器人的最新状态
    latest_data = df.sort_values('Timestamp').groupby('Robot_ID').last().reset_index()
    
    # 响应式布局：PC端5列，移动端2列
    # 使用CSS媒体查询自动适配，这里创建5列但移动端会自动调整
    cols = st.columns(5)
    for idx, row in latest_data.iterrows():
        col_idx = idx % 5
        
        status = row['Status']
        if status == 'Running':
            status_class = 'status-running'
            status_color = '#00ff41'
            status_icon = '✓'
        elif status == 'Warning':
            status_class = 'status-warning'
            status_color = '#ffd700'
            status_icon = '⚠'
        else:  # Error
            status_class = 'status-error'
            status_color = '#ff0000'
            status_icon = '✕'
        
        with cols[col_idx]:
            st.markdown(f"""
            <div class="metric-card {status_class}">
                <div class="robot-name">{row['Robot_ID']}</div>
                <div class="status-text" style="color: {status_color};">{status_icon} {status}</div>
                <div class="metric-value">温度: {row['Motor_Temperature']:.1f}°C</div>
                <div class="metric-value">振动: {row['Vibration_Level']:.2f} mm/s</div>
                <div class="metric-value">负载: {row['Current_Load']:.2f} A</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ============ 2. 单机深度分析 ============
    st.sidebar.markdown("<h2 style='color: #00d4ff;'>🔍 单机分析</h2>", unsafe_allow_html=True)
    
    # 侧边栏选择机器人
    robot_list = sorted(df['Robot_ID'].unique())
    selected_robot = st.sidebar.selectbox(
        "选择机器人",
        robot_list,
        index=0
    )
    
    # 筛选该机器人的数据
    robot_df = df[df['Robot_ID'] == selected_robot].sort_values('Timestamp')
    
    # 性能优化：如果数据点太多，进行采样（保留最近的数据和关键点）
    MAX_POINTS = 2000  # 最大显示点数
    if len(robot_df) > MAX_POINTS:
        # 保留最近的数据 + 均匀采样历史数据
        recent_data = robot_df.tail(500)  # 最近500个点
        historical_data = robot_df.iloc[:-500]
        if len(historical_data) > 0:
            # 均匀采样历史数据
            step = max(1, len(historical_data) // (MAX_POINTS - 500))
            sampled_historical = historical_data.iloc[::step]
            robot_df = pd.concat([sampled_historical, recent_data]).sort_values('Timestamp')
    
    st.markdown(f"<h2>📈 {selected_robot} - 历史趋势分析</h2>", unsafe_allow_html=True)
    
    # 创建双子图 - 移动端优化
    # 将Y轴标题信息直接写在子图标题里
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('电机温度 (°C) - 趋势图', '振动水平 (mm/s) - 趋势图'),
        vertical_spacing=0.2,  # 紧凑间距
        row_heights=[0.5, 0.5],
        specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
    )
    
    # 优化子图标题字体大小（移动端友好）
    fig.update_annotations(font_size=12)
    
    # ===== 温度图表 =====
    # 警戒线阈值
    TEMP_THRESHOLD = 80
    VIB_THRESHOLD = 5
    
    # 温度折线
    fig.add_trace(
        go.Scatter(
            x=robot_df['Timestamp'],
            y=robot_df['Motor_Temperature'],
            mode='lines',
            name='温度',
            line=dict(color='#00d4ff', width=2),
            hovertemplate='<b>时间</b>: %{x}<br><b>温度</b>: %{y:.2f}°C<extra></extra>'
        ),
        row=1, col=1
    )
    
    # 温度警戒线
    fig.add_hline(
        y=TEMP_THRESHOLD,
        line_dash="dash",
        line_color="red",
        line_width=1.5,
        annotation_text=f"{TEMP_THRESHOLD}°C",  # 简化注释文字
        annotation_position="right",
        annotation_font=dict(size=9, color='red'),  # 字体调小
        row=1, col=1
    )
    
    # 超过警戒线的区域高亮
    over_temp = robot_df[robot_df['Motor_Temperature'] > TEMP_THRESHOLD]
    if not over_temp.empty:
        fig.add_trace(
            go.Scatter(
                x=over_temp['Timestamp'],
                y=over_temp['Motor_Temperature'],
                mode='markers',
                name='超温',
                marker=dict(color='red', size=8, symbol='x'),
                hovertemplate='<b>⚠️ 超温</b><br>时间: %{x}<br>温度: %{y:.2f}°C<extra></extra>'
            ),
            row=1, col=1
        )
    
    # ===== 振动图表 =====
    # 振动折线
    fig.add_trace(
        go.Scatter(
            x=robot_df['Timestamp'],
            y=robot_df['Vibration_Level'],
            mode='lines',
            name='振动',
            line=dict(color='#00ff41', width=2),
            hovertemplate='<b>时间</b>: %{x}<br><b>振动</b>: %{y:.3f} mm/s<extra></extra>'
        ),
        row=2, col=1
    )
    
    # 振动警戒线
    fig.add_hline(
        y=VIB_THRESHOLD,
        line_dash="dash",
        line_color="red",
        line_width=1.5,
        annotation_text=f"{VIB_THRESHOLD} mm/s",  # 简化注释文字
        annotation_position="right",
        annotation_font=dict(size=9, color='red'),  # 字体调小
        row=2, col=1
    )
    
    # 超过警戒线的区域高亮
    over_vib = robot_df[robot_df['Vibration_Level'] > VIB_THRESHOLD]
    if not over_vib.empty:
        fig.add_trace(
            go.Scatter(
                x=over_vib['Timestamp'],
                y=over_vib['Vibration_Level'],
                mode='markers',
                name='超振动',
                marker=dict(color='red', size=8, symbol='x'),
                hovertemplate='<b>⚠️ 超振动</b><br>时间: %{x}<br>振动: %{y:.3f} mm/s<extra></extra>'
            ),
            row=2, col=1
        )
    
    # 更新布局 - 移动端深度优化
    fig.update_layout(
        # 1. 标题和边距调整 - 极窄边距，利用屏幕空间
        margin=dict(l=10, r=10, t=30, b=10),
        title=dict(font=dict(size=14)),
        
        # 2. 图例移到顶部，不占右边位置
        showlegend=True,
        legend=dict(
            orientation="h",    # 水平排列
            yanchor="bottom",
            y=1.02,             # 放在图表上方
            xanchor="right",
            x=1,
            font=dict(size=9),  # 图例字体更小
            bgcolor='rgba(0, 0, 0, 0.5)',  # 半透明背景
            bordercolor='rgba(255, 255, 255, 0.2)',
            borderwidth=1
        ),
        
        # 3. 背景透明化，融合暗色主题
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        
        # 4. 自动高度 - 两个子图，每个约300px
        height=600,  # 两个图表各300px
        
        # 5. 其他设置
        hovermode='x unified',
        font=dict(color='#ffffff', family='Arial, sans-serif', size=10),
    )
    
    # 更新坐标轴 - 移动端优化
    # 去掉所有轴标题，信息已包含在子图标题中
    
    # X轴 - 两个图表都显示，但去掉标题
    fig.update_xaxes(
        showgrid=True,
        gridcolor='rgba(255, 255, 255, 0.1)',
        title=None,  # 去掉X轴标题
        tickfont=dict(size=9),  # 刻度字体调小
        row=1, col=1
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor='rgba(255, 255, 255, 0.1)',
        title=None,  # 去掉X轴标题
        tickfont=dict(size=9),  # 刻度字体调小
        row=2, col=1
    )
    
    # Y轴 - 去掉标题，刻度字体调小
    fig.update_yaxes(
        showgrid=True,
        gridcolor='rgba(255, 255, 255, 0.1)',
        title=None,  # 去掉Y轴标题，信息已在子图标题中
        tickfont=dict(size=9),  # 刻度字体调小
        row=1, col=1
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor='rgba(255, 255, 255, 0.1)',
        title=None,  # 去掉Y轴标题，信息已在子图标题中
        tickfont=dict(size=9),  # 刻度字体调小
        row=2, col=1
    )
    
    # 移动端优化的图表配置 - 彻底隐藏工具栏
    config = {
        'displayModeBar': False,  # 彻底隐藏工具栏
        'staticPlot': False,
        'scrollZoom': False,
        'responsive': True  # 响应式
    }
    
    st.plotly_chart(fig, use_container_width=True, config=config)
    
    # ============ 3. 故障预警列表 ============
    st.markdown("---")
    st.markdown("<h2>⚠️ 故障预警记录</h2>", unsafe_allow_html=True)
    
    # 筛选 Warning 和 Error 状态
    alert_df = df[df['Status'].isin(['Warning', 'Error'])].sort_values('Timestamp', ascending=False)
    
    if not alert_df.empty:
        # 显示统计 - 移动端优化（响应式列布局）
        warning_count = len(alert_df[alert_df['Status'] == 'Warning'])
        error_count = len(alert_df[alert_df['Status'] == 'Error'])
        
        # PC端3列，移动端自动调整为单列
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总预警数", len(alert_df), delta=None)
        with col2:
            st.metric("警告 (Warning)", warning_count, delta=None)
        with col3:
            st.metric("错误 (Error)", error_count, delta=None, delta_color="inverse")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 格式化显示
        display_df = alert_df[['Timestamp', 'Robot_ID', 'Status', 'Motor_Temperature', 
                                'Vibration_Level', 'Current_Load']].copy()
        display_df.columns = ['时间', '机器人ID', '状态', '电机温度(°C)', '振动(mm/s)', '电流负载(A)']
        
        # 应用颜色样式
        def highlight_status(row):
            if row['状态'] == 'Error':
                return ['background-color: rgba(255, 0, 0, 0.2)'] * len(row)
            elif row['状态'] == 'Warning':
                return ['background-color: rgba(255, 215, 0, 0.2)'] * len(row)
            return [''] * len(row)
        
        styled_df = display_df.style.apply(highlight_status, axis=1)
        st.dataframe(styled_df, use_container_width=True, height=400)
    else:
        st.success("✅ 所有机器人运行正常，暂无预警记录")
    
    # 侧边栏统计信息
    st.sidebar.markdown("---")
    st.sidebar.markdown("<h3 style='color: #00d4ff;'>📊 数据统计</h3>", unsafe_allow_html=True)
    st.sidebar.info(f"""
    **数据范围**  
    起始: {df['Timestamp'].min().strftime('%Y-%m-%d %H:%M')}  
    结束: {df['Timestamp'].max().strftime('%Y-%m-%d %H:%M')}
    
    **数据量**  
    总记录数: {len(df):,}  
    机器人数: {df['Robot_ID'].nunique()}
    """)

except FileNotFoundError:
    st.error("❌ 错误：未找到文件 'robot_sensor_data.csv'")
    st.info("请确保 CSV 文件在当前目录下，或先运行 generate_data.py 生成数据。")
except Exception as e:
    st.error(f"❌ 发生错误: {str(e)}")

