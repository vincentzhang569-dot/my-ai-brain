import streamlit as st
from openai import OpenAI
import pdfplumber

# --- 1. 页面配置 (移动端优先) ---
st.set_page_config(
    page_title="工业智脑 Mobile",
    page_icon="🤖",
    layout="wide", # 虽然是宽屏，但在手机上会自动适配
    initial_sidebar_state="collapsed" # 强制收起侧边栏，因为我们不需要它了
)

# --- 2. 注入黑科技 CSS (让网页像原生App) ---
st.markdown("""
<style>
    /* 1. 隐藏 Streamlit 自带的汉堡菜单和右上角红线 */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 2. 调整顶部空白，让标题往上顶，手机屏幕寸土寸金 */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem; /* 留出底部输入框的位置 */
    }
    
    /* 3. 美化聊天气泡 */
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }
    
    /* 4. 让输入框更像微信 */
    .stChatInput {
        position: fixed;
        bottom: 0px;
        z-index: 1000;
        background-color: white;
        padding-bottom: 20px;
    }
    
    /* 5. 标题样式 */
    .mobile-header {
        font-size: 1.8rem; 
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #FF4B4B, #FF914D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 核心函数：读取PDF ---
def read_pdf_text(uploaded_file) -> str:
    text_parts = []
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
        return "\n".join(text_parts).strip()
    except Exception as e:
        st.error(f"解析PDF出错了: {e}")
        return ""

# --- 初始化状态 ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "🤖 您好！我是您的工业技术顾问。请点击上方的 **'设置与文档'** 上传手册。"}]
if "current_file" not in st.session_state:
    st.session_state.current_file = ""
if "pdf_content" not in st.session_state:
    st.session_state.pdf_content = ""

# --- 3. 界面布局 (移动端逻辑) ---

# 顶部标题 (渐变色酷炫标题)
st.markdown('<p class="mobile-header">INDUSTRIAL AI BRAIN</p>', unsafe_allow_html=True)

# === 核心改变：用折叠面板代替侧边栏 ===
# 逻辑：如果没有 Key 或者没上传文件，这个面板默认展开 (expanded=True)，逼着用户去填
show_expander = not st.session_state.get('api_key_input') or not st.session_state.pdf_content

with st.expander("⚙️ 设置与文档 (点击收起/展开)", expanded=show_expander):
    st.caption("请先完成以下配置以激活 AI")
    
    # 1. API Key 输入
    api_key = st.text_input("1. 输入 SiliconFlow Key", type="password", key="api_key_input")
    
    # 2. 文件上传
    uploaded_file = st.file_uploader("2. 上传 PDF 技术手册", type=["pdf"])
    
    # 3. 参数调节 (一行放两个，节省空间)
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        temperature = st.slider("创造力", 0.0, 1.0, 0.3)
    with col_p2:
        if st.button("清空对话", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    # 处理文件读取
    if uploaded_file:
        if st.session_state.current_file != uploaded_file.name:
            with st.spinner("📄 文档解析中..."):
                text = read_pdf_text(uploaded_file)
                st.session_state.pdf_content = text
                st.session_state.current_file = uploaded_file.name
            st.success(f"已加载: {uploaded_file.name}")

# --- 4. 聊天区域 ---

# 动态提示：如果没传文件，显示一个醒目的警告
if not st.session_state.pdf_content:
    st.info("👆 请点击上方折叠面板，上传 PDF 文档开始对话。")

# 显示聊天记录
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 5. 处理输入 ---
if prompt := st.chat_input("输入技术问题..."):
    if not api_key:
        st.toast("⚠️ 请先在顶部设置中输入 API Key")
        st.stop()
        
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prompt Engineering
    pdf_text = st.session_state.pdf_content
    if pdf_text:
        system_prompt = f"""
        你是一个工业技术专家。请基于以下文档内容回答问题。
        格式要求：使用简练的语言，适合手机阅读。关键步骤请分点说明。
        
        【文档片段】：
        {pdf_text[:8000]} 
        """
    else:
        system_prompt = "你是一个AI助手。请用简练的语言回答问题。"

    messages_for_api = [{"role": "system", "content": system_prompt}] + st.session_state.messages

    try:
        client = OpenAI(api_key=api_key, base_url="https://api.siliconflow.cn/v1")
        
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model="Qwen/Qwen2.5-7B-Instruct",
                messages=messages_for_api,
                stream=True,
                temperature=temperature,
            )
            response = st.write_stream(stream)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

    except Exception as e:
        st.error(f"网络错误: {e}")

