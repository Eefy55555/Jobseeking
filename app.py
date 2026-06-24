import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# 1. 页面基本配置与字体样式（新细明体 + Calibri）
# ==========================================
st.set_page_config(page_title="2026秋招进展汇报", page_icon="💼", layout="wide")

# 注入自定义 CSS 调节字体和样式，确保长辈阅读舒适（字号偏大，行距适中）
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
        font-size: 26px !important; /* 数字字号从 35px 缩减到 26px，防止在手机上折行 */
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
# 2. 本地数据读取与处理
# ==========================================
@st.cache_data
def load_data():
    file_path = "https://docs-import-export-1251316161.cos.ap-guangzhou.myqcloud.com/export/docx/RJuBlkOSCAOP/version_0_144115226059951793.json_144115226059951793_1c05e9e8-eb65-c786-fce2-cc5ef23f1941.xlsx?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKID8GWineS8xy0uqtmhiaKxNiuwtywncHya%2F20260624%2Fap-guangzhou%2Fs3%2Faws4_request&X-Amz-Date=20260624T023225Z&X-Amz-Expires=1800&X-Amz-SignedHeaders=host&response-content-disposition=attachment%3Bfilename%3D%222026fall.xlsx%22%3Bfilename%2A%3DUTF-8%27%272026fall.xlsx&response-content-type=&X-Amz-Signature=720eb2024b66d5373bf3ba13aa0f1e3c997a92ea577ea48b649984b8d4a3c59b"  # 严格读取本地同文件夹下的 Excel
    try:
        # 明确只读取名为 "2026fall" 的第一个 sheet
        df = pd.read_excel(file_path, sheet_name="2026fall")
        
        # 清洗数据：只保留需要的 5 列核心字段
        core_columns = ['类别', '投递时间', '公司/单位名称', '岗位', '时间节点', '进展']
        existing_cols = [col for col in core_columns if col in df.columns]
        df = df[existing_cols].copy()
        
        # 填充空值，避免网页显示 NaN
        for col in df.columns:
            df[col] = df[col].fillna('')
        # 优化逻辑：将投递时间只保留到年月日（YYYY-MM-DD）
        if '投递时间' in df.columns:
            df['投递时间'] = pd.to_datetime(df['投递时间'], errors='coerce').dt.strftime('%Y-%m-%d').fillna(df['投递时间'])
            
        return df
    except Exception as e:
        st.error(f"本地 Excel 文件读取失败！请检查 `2026fall.xlsx` 是否与本程序放在同一个文件夹内。错误信息: {e}")
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
    
    # 展现本地最新的同步时间，本地保存后刷新网页即刻更新
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.caption(f"⏱️ 本地数据最近一次刷新同步时间：{current_time}")
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
    # 4. 一键复制微信汇报文本
    # ==========================================
    st.subheader("💬 简报")
    
    # 筛选出最近有最新“进展”的2家单位放入微信草稿
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

    # 优化逻辑：将复制框改为精美的文字布告栏（使用带有提示色块的 info 样式）
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
            
