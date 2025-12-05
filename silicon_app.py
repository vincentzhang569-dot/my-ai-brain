import streamlit as st
from openai import OpenAI
import pdfplumber

# 1. 页面基本设置
st.set_page_config(page_title="我的AI知识库(PDF版)", page_icon="📚")
st.title("📚 个人知识库助手 (硅基流动版)")
st.caption("上传PDF，AI 就能基于文档回答你的问题！")

# --- 核心函数：读取PDF ---
def read_pdf_text(uploaded_file) -> str:
    """读取 PDF 全部文本内容"""
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

# --- 关键修复：初始化所有状态变量 ---
# (之前就是缺了这里，导致报错)
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "你好！请先在左侧上传 PDF，然后问我关于文档的问题。"}]
if "current_file" not in st.session_state:
    st.session_state.current_file = ""
if "pdf_content" not in st.session_state:
    st.session_state.pdf_content = ""

# 2. 侧边栏设置
with st.sidebar:
    st.header("1. 身份验证")
    api_key = st.text_input("请输入硅基流动 API Key (sk-开头)", type="password")
    
    st.divider()
    
    st.header("2. 上传文档")
    uploaded_file = st.file_uploader("请上传 PDF 文档", type=["pdf"])
    
    # 如果上传了文件，就读取内容
    if uploaded_file:
        # 修复后的逻辑：先确保 current_file 存在，再比较
        if st.session_state.current_file != uploaded_file.name:
            with st.spinner("正在读取文档，请稍等..."):
                text = read_pdf_text(uploaded_file)
                st.session_state.pdf_content = text
                st.session_state.current_file = uploaded_file.name
                st.success(f"✅ 读取成功！共 {len(text)} 字")
    else:
        st.session_state.pdf_content = ""
        st.session_state.current_file = ""

# 3. 显示历史聊天
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 4. 处理用户输入
if prompt := st.chat_input("请输入你的问题..."):
    if not api_key:
        st.error("请先在左侧填入 API Key！")
        st.stop()

    # 显示用户问题
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # --- 构建提示词 ---
    pdf_text = st.session_state.pdf_content
    
    if pdf_text:
        # 为了防止免费模型字数超限，截取前8000字
        system_prompt = f"""
        你是一个专业的文档助手。请完全基于下方的【文档内容】来回答用户的问题。
        如果【文档内容】中没有提到答案，请直接说“文档中未提及”。
        
        【文档内容】：
        {pdf_text[:8000]} 
        """ 
    else:
        system_prompt = "你是一个AI助手，请回答用户的问题。"

    # 将系统提示词加入对话列表的开头
    messages_for_api = [{"role": "system", "content": system_prompt}] + st.session_state.messages

    # --- 连接 AI ---
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.siliconflow.cn/v1"
        )

        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model="Qwen/Qwen2.5-7B-Instruct",
                messages=messages_for_api,
                stream=True,
            )
            response = st.write_stream(stream)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

    except Exception as e:
        st.error(f"连接出错了: {e}")
