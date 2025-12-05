import streamlit as st
from openai import OpenAI
import pdfplumber
from datetime import datetime
from io import BytesIO
try:
    from docx import Document
    from docx.shared import Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# --- 1. 页面配置 (移动端优先) ---
st.set_page_config(
    page_title="工业智脑 Mobile",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. 移动端优化 CSS (原生App级体验) ---
st.markdown("""
<style>
    /* ========== 基础清理 ========== */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* ========== 移动端响应式布局 ========== */
    @media (max-width: 768px) {
        /* 主容器优化 */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 6rem;
            padding-left: 1rem;
            padding-right: 1rem;
            max-width: 100%;
        }
        
        /* 标题优化 - 移动端更小 */
        .mobile-header {
            font-size: 1.5rem !important;
            margin-bottom: 0.8rem;
        }
        
        /* 聊天消息气泡优化 */
        .stChatMessage {
            border-radius: 18px;
            padding: 12px 16px;
            margin-bottom: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        
        /* 用户消息样式 */
        .stChatMessage[data-testid="user"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: 20%;
        }
        
        /* AI消息样式 */
        .stChatMessage[data-testid="assistant"] {
            background: #f8f9fa;
            color: #333;
            margin-right: 20%;
        }
        
        /* 输入框固定在底部 */
        .stChatInput {
            position: fixed !important;
            bottom: 0 !important;
            left: 0 !important;
            right: 0 !important;
            z-index: 1000;
            background: white;
            padding: 12px 16px;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
            border-top: 1px solid #e0e0e0;
        }
        
        .stChatInput > div > div {
            border-radius: 25px;
            padding: 10px 20px;
            font-size: 16px; /* 防止iOS自动缩放 */
        }
        
        /* 按钮优化 - 触摸友好 */
        .stButton > button {
            width: 100%;
            height: 44px; /* iOS推荐的最小触摸目标 */
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        /* 滑块优化 */
        .stSlider {
            padding: 10px 0;
        }
        
        /* 文件上传器优化 - 仅移动端 */
        .stFileUploader {
            padding: 15px;
            border: 2px dashed #667eea;
            border-radius: 12px;
            background: #f8f9ff;
        }
        
        /* 文件上传器标签文字优化 */
        .stFileUploader label {
            line-height: 1.5;
            word-break: break-word;
        }
        
        /* 折叠面板优化 */
        .streamlit-expanderHeader {
            font-size: 16px;
            font-weight: 600;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
        }
        
        /* 文本输入框优化 */
        .stTextInput > div > div > input {
            font-size: 16px; /* 防止iOS自动缩放 */
            padding: 12px;
            border-radius: 10px;
        }
        
        /* 成功/错误消息优化 */
        .stSuccess, .stInfo, .stWarning, .stError {
            border-radius: 10px;
            padding: 12px;
            margin: 10px 0;
        }
        
        /* 列布局优化 - 移动端单列 */
        .stColumn {
            padding: 0 5px;
        }
    }
    
    /* ========== PC端保持宽屏体验 ========== */
    @media (min-width: 769px) {
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }
        
        .mobile-header {
            font-size: 2.2rem;
        }
        
        /* PC端文件上传器优化 - 防止文字重叠 */
        .stFileUploader {
            padding: 20px;
            line-height: 1.6;
            min-height: auto;
        }
        
        /* 文件上传器标签文字 */
        .stFileUploader label,
        .stFileUploader label p {
            line-height: 1.6 !important;
            white-space: normal !important;
            word-break: break-word !important;
            display: block !important;
            margin-bottom: 8px !important;
            height: auto !important;
            overflow: visible !important;
        }
        
        /* 文件上传器内部容器 */
        .stFileUploader > div {
            line-height: 1.6;
            height: auto;
        }
        
        /* 文件上传器提示文字 */
        .stFileUploader small,
        .stFileUploader .stMarkdown {
            line-height: 1.5;
            display: block;
            margin-top: 8px;
        }
        
        /* PC端文本输入框优化 */
        .stTextInput label {
            line-height: 1.5;
            white-space: normal;
        }
        
        /* PC端折叠面板内容优化 */
        .streamlit-expanderContent {
            padding: 1rem;
        }
    }
    
    /* ========== 通用样式 ========== */
    .mobile-header {
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 1.5rem;
        letter-spacing: 1px;
    }
    
    /* PC端通用文字优化 - 防止重叠 */
    @media (min-width: 769px) {
        /* 所有标签文字 */
        label, label p {
            line-height: 1.5 !important;
            white-space: normal !important;
            height: auto !important;
        }
        
        /* Streamlit组件文字 */
        .stMarkdown, .stMarkdown p {
            line-height: 1.6;
            white-space: normal;
        }
    }
    
    /* 卡片式容器 */
    .card-container {
        background: white;
        border-radius: 16px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    
    /* 滚动条美化 */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    
    /* 加载动画优化 */
    .stSpinner > div {
        border-color: #667eea transparent transparent transparent;
    }
    
    /* 移动端触摸反馈 */
    @media (max-width: 768px) {
        * {
            -webkit-tap-highlight-color: rgba(102, 126, 234, 0.2);
        }
        
        /* 防止双击缩放 */
        * {
            touch-action: manipulation;
        }
    }
    
    /* 移动端安全区域适配 (iPhone X 等) */
    @supports (padding: max(0px)) {
        @media (max-width: 768px) {
            .stChatInput {
                padding-bottom: max(12px, env(safe-area-inset-bottom));
            }
        }
    }
    
    /* ========== 快捷指令按钮样式 ========== */
    .quick-actions-container {
        display: flex;
        gap: 10px;
        margin-bottom: 20px;
        flex-wrap: wrap;
        justify-content: center;
    }
    
    @media (max-width: 768px) {
        .quick-actions-container {
            gap: 8px;
            margin-bottom: 15px;
        }
        
        /* 移动端快捷指令按钮优化 */
        .stButton > button[kind="secondary"] {
            font-size: 13px;
            padding: 10px 12px;
        }
    }
    
    /* 下载按钮样式 */
    .download-btn-container {
        margin-top: 20px;
        padding: 15px;
        background: #f8f9fa;
        border-radius: 12px;
        text-align: center;
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

# --- 生成对话记录 Markdown ---
def generate_markdown_export(messages, doc_name=""):
    """生成Markdown格式的对话记录"""
    md_content = f"""# 工业智脑对话记录

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**文档名称**: {doc_name if doc_name else '未上传文档'}

---

"""
    for i, msg in enumerate(messages, 1):
        role = "用户" if msg["role"] == "user" else "AI助手"
        md_content += f"## {i}. {role}\n\n"
        md_content += f"{msg['content']}\n\n"
        md_content += "---\n\n"
    
    return md_content

# --- 生成对话记录 Word ---
def generate_word_export(messages, doc_name=""):
    """生成Word格式的对话记录"""
    if not DOCX_AVAILABLE:
        return None
    
    doc = Document()
    
    # 设置文档样式
    style = doc.styles['Normal']
    font = style.font
    font.name = '微软雅黑'
    font.size = Pt(11)
    
    # 标题
    title = doc.add_heading('工业智脑对话记录', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title.runs[0]
    title_run.font.name = '微软雅黑'
    title_run.font.size = Pt(18)
    title_run.font.bold = True
    
    # 元信息
    meta_para = doc.add_paragraph()
    meta_para.add_run(f'生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}').font.name = '微软雅黑'
    meta_para = doc.add_paragraph()
    meta_para.add_run(f'文档名称: {doc_name if doc_name else "未上传文档"}').font.name = '微软雅黑'
    doc.add_paragraph('')
    
    # 分隔线
    sep_para = doc.add_paragraph('─' * 60)
    sep_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph('')
    
    # 对话内容
    for i, msg in enumerate(messages, 1):
        role = "用户" if msg["role"] == "user" else "AI助手"
        heading = doc.add_heading(f'{i}. {role}', level=1)
        heading.alignment = WD_ALIGN_PARAGRAPH.LEFT
        heading_run = heading.runs[0]
        heading_run.font.name = '微软雅黑'
        heading_run.font.size = Pt(14)
        heading_run.font.bold = True
        heading_run.font.color.rgb = RGBColor(102, 126, 234) if msg["role"] == "user" else RGBColor(0, 0, 0)
        
        # 添加内容
        content = msg['content']
        paragraphs = content.split('\n')
        for para in paragraphs:
            if para.strip():
                p = doc.add_paragraph()
                p.style.font.name = '微软雅黑'
                # 处理Markdown加粗
                parts = para.split('**')
                for idx, part in enumerate(parts):
                    run = p.add_run(part)
                    run.font.name = '微软雅黑'
                    if idx % 2 == 1:  # 奇数索引是加粗内容
                        run.bold = True
                if not parts:
                    run = p.add_run(para)
                    run.font.name = '微软雅黑'
        
        doc.add_paragraph('')
        sep_para = doc.add_paragraph('─' * 60)
        sep_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph('')
    
    # 保存到BytesIO
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 初始化状态 ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "🤖 您好！我是您的工业技术顾问。\n\n**快速开始：**\n1. 点击上方 ⚙️ **设置与文档** 展开配置面板\n2. 输入您的 SiliconFlow API Key\n3. 上传 PDF 技术手册\n4. 开始提问！"}]
if "current_file" not in st.session_state:
    st.session_state.current_file = ""
if "pdf_content" not in st.session_state:
    st.session_state.pdf_content = ""
if "pending_quick_action" not in st.session_state:
    st.session_state.pending_quick_action = None

# --- 3. 界面布局 (移动端优化) ---

# 顶部标题 (渐变色酷炫标题)
st.markdown('<p class="mobile-header">🏭 INDUSTRIAL AI BRAIN</p>', unsafe_allow_html=True)

# === 设置面板 (移动端友好的折叠设计) ===
show_expander = not st.session_state.get('api_key_input') or not st.session_state.pdf_content

with st.expander("⚙️ 设置与文档", expanded=show_expander):
    # 状态指示器
    status_col1, status_col2 = st.columns(2)
    with status_col1:
        api_status = "✅" if st.session_state.get('api_key_input') else "❌"
        st.caption(f"API Key: {api_status}")
    with status_col2:
        doc_status = "✅" if st.session_state.pdf_content else "❌"
        st.caption(f"文档: {doc_status}")
    
    st.divider()
    
    # 1. API Key 输入
    api_key = st.text_input(
        "🔑 SiliconFlow API Key", 
        type="password", 
        key="api_key_input",
        placeholder="请输入 sk- 开头的密钥",
        help="在 SiliconFlow 官网获取您的 API Key"
    )
    
    # 2. 文件上传 (移动端优化)
    st.markdown("**📄 上传技术手册**")
    uploaded_file = st.file_uploader(
        "支持 PDF 格式", 
        type=["pdf"],
        help="上传您的技术手册、操作指南或故障排除文档"
    )
    
    # 显示文档信息
    if st.session_state.pdf_content:
        doc_length = len(st.session_state.pdf_content)
        st.success(f"📚 当前文档: **{st.session_state.current_file}**")
        st.caption(f"📊 文档大小: {doc_length:,} 字符 | 约 {doc_length//1000}K tokens")
    
    st.divider()
    
    # 3. 高级设置 (移动端紧凑布局)
    st.markdown("**⚙️ 高级设置**")
    col_p1, col_p2 = st.columns([2, 1])
    with col_p1:
        temperature = st.slider(
            "🎨 创造力 (Temperature)", 
            0.0, 1.0, 0.3,
            help="数值越低越严谨，数值越高越有创造性"
        )
    with col_p2:
        st.markdown("<br>", unsafe_allow_html=True)  # 对齐按钮
        if st.button("🗑️ 清空", use_container_width=True, help="清空所有对话记录"):
            st.session_state.messages = [{"role": "assistant", "content": "🤖 对话历史已清空，请重新提问。"}]
            st.rerun()

    # 处理文件读取
    if uploaded_file:
        if st.session_state.current_file != uploaded_file.name:
            with st.spinner("📄 正在解析文档，请稍候..."):
                text = read_pdf_text(uploaded_file)
                st.session_state.pdf_content = text
                st.session_state.current_file = uploaded_file.name
            st.success(f"✅ 文档加载成功: **{uploaded_file.name}**")
            st.balloons()  # 成功提示动画

# --- 4. 聊天区域 (移动端优化) ---

# 动态状态提示
if not st.session_state.get('api_key_input'):
    st.warning("⚠️ 请先在设置中输入 API Key")
elif not st.session_state.pdf_content:
    st.info("📄 请上传 PDF 文档以开始智能问答")
else:
    st.success("✅ 一切就绪，可以开始提问了！")

# === 快捷指令按钮 (工业现场一键操作) ===
if st.session_state.get('api_key_input') and st.session_state.pdf_content:
    st.markdown("**⚡ 快捷指令**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 全文摘要", use_container_width=True, help="一键生成文档全文摘要"):
            st.session_state.pending_quick_action = "请为这份文档生成一份详细的全文摘要，包括主要章节、核心内容和关键要点。"
            st.rerun()
    
    with col2:
        if st.button("🔧 故障诊断", use_container_width=True, help="快速进入故障排查模式"):
            st.session_state.pending_quick_action = "请列出这份文档中涉及的所有故障代码、故障原因和对应的解决方案。如果文档中没有相关内容，请说明。"
            st.rerun()
    
    with col3:
        if st.button("⚠️ 安全须知", use_container_width=True, help="查看安全操作注意事项"):
            st.session_state.pending_quick_action = "请提取这份文档中所有关于安全操作、注意事项、警告信息的内容，并按重要性排序。"
            st.rerun()

# 显示聊天记录 (移动端优化)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# === 对话记录下载功能 ===
if len(st.session_state.messages) > 1:  # 至少有用户和AI的对话
    st.divider()
    st.markdown("**💾 导出对话记录**")
    
    download_col1, download_col2 = st.columns(2)
    
    with download_col1:
        # Markdown下载
        md_content = generate_markdown_export(
            st.session_state.messages, 
            st.session_state.current_file
        )
        st.download_button(
            label="📄 下载 Markdown",
            data=md_content,
            file_name=f"对话记录_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            use_container_width=True,
            help="下载为Markdown格式，适合文档管理"
        )
    
    with download_col2:
        # Word下载
        if DOCX_AVAILABLE:
            word_buffer = generate_word_export(
                st.session_state.messages,
                st.session_state.current_file
            )
            if word_buffer:
                st.download_button(
                    label="📝 下载 Word",
                    data=word_buffer,
                    file_name=f"对话记录_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                    help="下载为Word格式，适合工单汇报"
                )
        else:
            st.info("💡 安装 python-docx 以支持Word导出\n`pip install python-docx`", icon="ℹ️")

# --- 5. 处理用户输入 (移动端优化) ---
# 处理快捷指令
prompt = None
if st.session_state.pending_quick_action:
    prompt = st.session_state.pending_quick_action
    st.session_state.pending_quick_action = None  # 清除标志

# 处理用户手动输入
user_input = st.chat_input("💬 输入技术问题...")
if user_input:
    prompt = user_input

if prompt:
    # 验证配置
    if not api_key:
        st.toast("⚠️ 请先在设置中输入 API Key", icon="⚠️")
        st.stop()
    
    if not st.session_state.pdf_content:
        st.toast("📄 请先上传 PDF 文档", icon="📄")
        st.stop()
        
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 构建系统提示词 (移动端优化 - 更简洁的回答)
    pdf_text = st.session_state.pdf_content
    if pdf_text:
        system_prompt = f"""你是一个专业的工业技术顾问，擅长分析技术文档。

【任务要求】：
1. 严格基于以下文档内容回答问题，不要编造信息
2. 回答要简洁明了，适合在手机上阅读
3. 使用 Markdown 格式，关键信息用 **加粗** 标注
4. 如果问题超出文档范围，明确告知"文档中未提及此内容"
5. 对于故障排查类问题，请按步骤列出解决方案

【文档内容】：
{pdf_text[:8000]}

请开始回答用户问题："""
    else:
        system_prompt = """你是一个AI助手。请用简洁、专业的语言回答问题。
回答要适合在手机上阅读，使用 Markdown 格式。"""

    messages_for_api = [{"role": "system", "content": system_prompt}] + st.session_state.messages

    # 调用AI API
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.siliconflow.cn/v1")
        
        with st.chat_message("assistant"):
            # 显示加载状态
            with st.spinner("🤔 AI 正在思考中..."):
                stream = client.chat.completions.create(
                    model="Qwen/Qwen2.5-7B-Instruct",
                    messages=messages_for_api,
                    stream=True,
                    temperature=temperature,
                )
                response = st.write_stream(stream)
        
        # 保存回复
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # 成功提示
        st.toast("✅ 回答完成", icon="✅")

    except Exception as e:
        error_msg = str(e)
        st.error(f"❌ 请求失败: {error_msg}")
        st.info("💡 请检查：1) API Key 是否正确 2) 网络连接是否正常 3) 账户余额是否充足")
        
        # 添加重试建议
        if "401" in error_msg or "Unauthorized" in error_msg:
            st.warning("🔑 API Key 验证失败，请检查密钥是否正确")
        elif "429" in error_msg or "rate limit" in error_msg.lower():
            st.warning("⏱️ 请求过于频繁，请稍后再试")


