import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# 1. 页面基本配置与字体样式（移动端优化版）
# ==========================================
st.set_page_config(page_title="2026秋招进展汇报", page_icon="💼", layout="wide")

# 注入自定义 CSS 调节字体和样式，确保长辈在手机和电脑上阅读都舒适
st.markdown("""
    <style>
    /* 基础全局字体与字号调整，更适合手机屏幕 */
    html, body, [class*="css"] {
        font-family: 'Calibri', 'PMingLiU', 'New MingLiU', '新细明体', sans-serif;
        font-size: 16px; /* 电脑和手机的通用基础字号，稍微调小 */
    }
    
    /* 数据大卡片（Metrics）的手机端瘦身 */
    .stMetric label {
        font-size: 16px !important; /* 指标名称字号调小 */
        font-weight: bold;
    }
    .stMetric div {
        font-size: 26px !important; /* 数字字号缩减到 26px，防止在手机上折行 */
    }
    
    /* 手机端时间轴的紧凑排版 */
    .timeline-item {
        padding: 10px 12px; /* 缩小内边距 */
        border-left: 3px solid #2e7d32;
        margin-left: 5px;
        margin-bottom: 10px;
        background-color: #f9f9f9;
        border-radius: 0 6px 6px 0;
    }
    .timeline-date {
        font-weight: bold;
        color: #2e7d32;
        font-size: 15px; /* 约定时间时点字号微调 */
    }
    .timeline-content {
        margin-top: 3px;
        color: #333333;
        font-size: 14px; /* 核心内容字号微调 */
        line-height: 1.4;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 在线数据读取与处理（飞书/公开直连终极无缝版）
# ==========================================
@st.cache_data(ttl=600)  # 每 10 分钟自动更新缓存，确保父母刷新能看到最新动态
def load_data():
    # 完美的飞书公开直连格式
    file_path = "https://qcns92zz60yw.feisku.cn/sheets/EUZ0sDCt6hDDNYtMCE9cGLSnnF5/download"

    import requests
    import io
    
    try:
        # 标准网络请求
        response = requests.get(file_path, timeout=15)
        
        # 直接读取第一个 sheet，无视工作表命名
        df = pd.read_excel(io.BytesIO(response.content), sheet_name=0)
        
        # 清除表头前后空格
        df.columns = df.columns.str.strip()
        
        # 清洗数据：只保留需要的核心字段
        core_columns = ['类别', '投递时间', '公司/单位名称', '岗位', '时间节点', '进展']
        existing_cols = [col for col in core_columns if col in df.columns]
        df = df[existing_cols].copy()
        
        # 填充空值
        for col in df.columns:
            df[col] = df[col].fillna('')
            
        # 优化逻辑：将投递时间只保留到年月日
        if '投递时间' in df.columns:
            df['投递时间'] = pd.to_datetime(df['投递时间'], errors='coerce').dt.strftime('%Y-%m-%d').fillna(df['投递时间'])
            
        return df
    except Exception as e:
        st.error(f"❌ 在线表格读取失败！错误信息: {e}")
        return None

df = load_data()

if df is not None:
    # ==========================================
    # 3. 顶部三大数据卡片计算
    # ==========================================
    total_applied = len(df)
    
    # 统计“正在推进中”的数量
    processing_count = len(df[(df['进展'] != '') & (~df['进展'].str.contains('投递|谢谢信|拒', na=False))])
    
    # 统计 Offer 数量
    offer_count = len(df[df['进展'].str.contains('Offer|录用|录取', na=False)])
    
    # 页面大标题
    st.title("💼 2026秋招求职进展汇报小站")
    st.subheader("给最亲爱的爸爸妈妈：我会及时向你们更新动态，不用担心哦！")
    
    # 展现云端最新的同步时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.caption(f"⏱️ 网页数据最近一次刷新时间：{current_time}")
    st.write("---")

    # 渲染大卡片
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="📊 已投递单位总数", value=f"{total_applied} 家")
    with col2:
        st.metric(label="⏳ 正在推进/面试中", value=f"{processing_count} 个")
    with col3:
        st.metric(label="🎉 已收获 Offer", value=f"{offer_count} 个", delta="还需努力！" if offer_count==0 else "太棒了！")

    st.write("---")

    # ==========================================
    # 4. 精美布告栏简报展示
    # ==========================================
    st.subheader("💬 简报")
    
    # 筛选出最近有最新“进展”的2家单位放入草稿
    recent_updates = df[df['进展'] != ''].head(2)
    update_text = ""
    for idx, row in recent_updates.iterrows():
        if row['时间节点']:
            update_text += f"- {row['公司/单位名称']}({row['岗位']})：【{row['进展']}】 ({row['时间节点']})\n"
        else:
            update_text += f"- {row['公司/单位名称']}({row['岗位']})：【{row['进展']}】\n"
    
    report_template = f"""爸爸妈妈，汇报一下我的求职进展：
目前我一共投递了 {total_applied} 家单位。其中有 {processing_count} 个岗位正在面试/测评推进中。

近期最新动态：
{update_text if update_text else '- 各项投递正在稳步推进，等待进一步通知；'}
我会继续努力的，你们在家里也要照顾好身体，不用为我担心！🥰"""

    # 展示为像布告栏一样的纯文字精美提示框
    st.info(report_template)

    st.write("---")

    # ==========================================
    # 5. 下方完整表格展现
    # ==========================================
    st.subheader("📌 投递进展总览表")
    
    display_cols = ['类别', '投递时间', '公司/单位名称', '岗位', '进展']
    existing_display_cols = [c for c in display_cols if c in df.columns]
    
    st.dataframe(df[existing_display_cols], use_container_width=True)

    st.write("---")
    
    # ==========================================
    # 6. 时间轴展示（核心：聚焦“时间节点”和“进展”）
    # ==========================================
    st.subheader("⏱️ 时间轴")
    
    # 筛选出有填写“时间节点”和“进展”的数据
    timeline_data = df[(df['时间节点'] != '') & (df['进展'] != '')]
    
    if len(timeline_data) == 0:
        st.info("目前暂无面试/新进展大动态，投递和测评正在稳步积累中！")
    else:
        for idx, row in timeline_data.iterrows():
            st.markdown(f"""
            <div class="timeline-item">
                <div class="timeline-date">📅 约定时点：{row['时间节点']}</div>
                <div class="timeline-content">
                    <b>{row['公司/单位名称']}</b> · {row['岗位']} <br>
                    核心进展：<span style="color: #2e7d32; font-weight: bold;">【{row['进展']}】</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
