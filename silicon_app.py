import streamlit as st
from openai import OpenAI
import pdfplumber

# --- 1. 页面配置 (浏览器标签页样式) ---
st.set_page_config(
    page_title="工业级智能文档助手", 
    page_icon="🤖", 
    layout="wide" # 关键：开启宽屏模式，显得大气
)

# --- 自定义 CSS (让页面变好看的魔法) ---
st.markdown("""
<style>
    .stChatInput {border-radius: 20px;} 
    .main-header {font-size: 2.5rem; color: #FF4B4B; font-weight: 700;}
    .sub-header {font-size: 1.2rem; color: #666;}
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
    st.session_state.messages = [{"role": "assistant", "content": "👋 您好！我是您的智能文档助手。请上传一份技术手册或简历，我来为您分析。"}]
if "current_file" not in st.session_state:
    st.session_state.current_file = ""
if "pdf_content" not in st.session_state:
    st.session_state.pdf_content = ""

# --- 布局分栏 (2列布局：左侧设置，右侧聊天) ---
col1, col2 = st.columns([1, 2]) # 左1右2的比例

# === 左侧：控制面板 ===
with col1:
    st.markdown('<p class="main-header">🤖 AI 智脑</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">基于 RAG 技术的垂直领域知识库</p>', unsafe_allow_html=True)
    
    with st.container(border=True): # 加个边框，显得专业
        st.subheader("1. 身份验证")
        api_key = st.text_input("SiliconFlow API Key", type="password", help="请输入sk-开头的密钥")
        
        st.subheader("2. 文档上传")
        uploaded_file = st.file_uploader("支持 PDF 格式", type=["pdf"])
        
        if uploaded_file:
            if st.session_state.current_file != uploaded_file.name:
                with st.spinner("🔄 正在深入阅读文档..."): # 增加加载动画
                    text = read_pdf_text(uploaded_file)
                    st.session_state.pdf_content = text
                    st.session_state.current_file = uploaded_file.name
                st.success(f"✅ 已解析: {uploaded_file.name}")
                st.info(f"📚 文档长度: {len(text)} 字符")
        
        st.subheader("3. 模型参数 (高级设置)")
        # 增加参数滑块，面试时演示这个显得很懂行
        temperature = st.slider("创造力 (Temperature)", 0.0, 1.0, 0.3, help="数值越低越严谨，数值越高越发散")
        
        if st.button("🗑️ 清空对话历史", use_container_width=True):
            st.session_state.messages = [{"role": "assistant", "content": "历史记录已清空，请重新提问。"}]
            st.rerun()

# === 右侧：聊天窗口 ===
with col2:
    st.container(height=600, border=True) # 固定高度，像微信聊天框一样
    
    # 显示聊天记录
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 处理输入
    if prompt := st.chat_input("请输入您的问题 (例如：这份文档的核心观点是什么？)"):
        if not api_key:
            st.toast("🔴 请先输入 API Key！") # 弹出式提示
            st.stop()
            
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # --- 专家级 Prompt (让AI变聪明的关键) ---
        pdf_text = st.session_state.pdf_content
        
        if pdf_text:
            # 这里的 Prompt 进行了升级，要求AI结构化输出
            system_prompt = f"""
            你是一个高级数据分析师和技术专家。用户上传了一份文档，内容如下。
            请严格基于文档内容回答问题。
            
            【回答要求】：
            1. **结构清晰**：使用 Markdown 格式，多用加粗、列表。
            2. **引用原文**：如果可能，请指出答案在文档中的大概位置。
            3. **专业客观**：不要臆测，如果文档没提，就说不知道。
            
            【文档片段】：
            {pdf_text[:10000]} 
            """
        else:
            system_prompt = "你是一个全能AI助手。请用专业、简洁的语言回答用户问题。"

        messages_for_api = [{"role": "system", "content": system_prompt}] + st.session_state.messages

        try:
            client = OpenAI(api_key=api_key, base_url="https://api.siliconflow.cn/v1")
            
            with st.chat_message("assistant"):
                stream = client.chat.completions.create(
                    model="Qwen/Qwen2.5-7B-Instruct",
                    messages=messages_for_api,
                    stream=True,
                    temperature=temperature, # 把滑块的值传进去
                )
                response = st.write_stream(stream)
            
            st.session_state.messages.append({"role": "assistant", "content": response})

        except Exception as e:
            st.error(f"网络连接错误: {e}")
