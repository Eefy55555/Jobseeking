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
# 2. 在线数据读取与处理（腾讯文档终极强攻版）
# ==========================================
@st.cache_data(ttl=600)  # 每 10 分钟自动更新缓存
def load_data():
    # 依然使用你的腾讯文档 Token 链接
    file_path = "https://docs.qq.com/excel/download?token=DUkp1QmxrT1NDQU9Q"
    
    import requests
    import io
    
    try:
        # 终极伪装：不仅伪装成现代浏览器，还带上完整的校验协议（让腾讯误以为是合法的下载动作）
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Referer": "https://docs.qq.com/sheet/DUkp1QmxrT1NDQU9Q"
        }
        
        # 强行发起请求
        response = requests.get(file_path, headers=headers, timeout=15)
        
        # 智能拦截排查：如果腾讯吐回来的不是真实的 Excel 数据流，而是报错网页，在这里直接抓出来
        if b"html" in response.content[:100].lower():
            st.error("🔒 腾讯文档海外安全策略限制：当前链接被防爬虫防火墙拦截。")
            st.info("💡 最快解决办法：如果您不想折腾飞书，可以直接用微信/手机号注册登录电脑版【石墨文档】(shimo.im)，把 Excel 导入进去并开启‘任何人可看’，将其下载链接贴过来，100% 不会被拦截，极度顺畅！")
            return None
            
        # 正常读取
        df = pd.read_excel(io.BytesIO(response.content), sheet_name=0)
        
        # 清除表头前后空格
        df.columns = df.columns.str.strip()
        
        # 清洗数据
        core_columns = ['类别', '投递时间', '公司/单位名称', '岗位', '时间节点', '进展']
        existing_cols = [col for col in core_columns if col in df.columns]
        df = df[existing_cols].copy()
        
        for col in df.columns:
            df[col] = df[col].fillna('')
            
        if '投递时间' in df.columns:
            df['投递时间'] = pd.to_datetime(df['投递时间'], errors='coerce').dt.strftime('%Y-%m-%d').fillna(df['投递时间'])
            
        return df
    except Exception as e:
        st.error(f"❌ 在线读取发生未知错误: {e}")
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
            
