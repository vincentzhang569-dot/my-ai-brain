import base64
import pdfplumber
import streamlit as st
from PIL import Image

from core.llm_client import SILICONFLOW_MODEL, get_client
from core.rag_bridge import build_vector_store, query_vector_store

# ================= 页面与样式 =================
st.set_page_config(
    page_title="工业智脑",
    page_icon="🤖",
    layout="wide",
)

# 保留暗色上传框修复与基础样式
st.markdown(
    """
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* 标题容器 */
    .main-header-container {
        text-align: center;
        margin-bottom: 40px;
        padding: 20px 0;
    }

    /* 英文标题：巨大、渐变、霸气 */
    .main-title-en {
        font-family: 'Arial Black', sans-serif;
        font-size: 3.5rem !important; /* 强制巨大 */
        font-weight: 900 !important;
        text-transform: uppercase;
        background: linear-gradient(135deg, #0052D4 0%, #4364F7 50%, #6FB1FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 2px;
        line-height: 1.2;
        margin-bottom: 10px;
    }

    /* 中文标题：清晰、深色、加粗 (修复看不清的问题) */
    .main-title-cn {
        font-family: "Microsoft YaHei", "SimHei", sans-serif;
        font-size: 2rem !important; /* 32px 左右 */
        font-weight: 700 !important;
        color: #333333 !important; /* 强制深灰，防止发白看不清 */
        letter-spacing: 5px;
        opacity: 1 !important; /* 禁止透明 */
    }

    /* 适配暗黑模式 (如果用户切换了主题) */
    @media (prefers-color-scheme: dark) {
        .main-title-cn {
            color: #E0E0E0 !important; /* 暗黑模式下变白 */
        }
    }

    /* 容器宽度适配 */
    @media (min-width: 769px) {
        .block-container {max-width: 1200px;}
    }
    @media (max-width: 768px) {
        .block-container {
            padding-top: 1rem;
            padding-bottom: 5rem;
            padding-left: 1rem;
            padding-right: 1rem;
            max-width: 100%;
        }
    }

    /* 侧边栏文字与输入 */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] button * {
        color: inherit !important;
    }

    /* --- 🚑 终极修复：侧边栏上传框 (强制黑底白字) --- */
    [data-testid="stSidebar"] [data-testid="stFileUploader"] {
        padding: 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
        background-color: #262730 !important;
        border: 1px dashed #666 !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] div,
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] span,
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] small,
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] label {
        color: #FFFFFF !important;
        opacity: 1 !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] svg {
        fill: #FFFFFF !important;
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
        background-color: #4b4b4b !important;
        color: #FFFFFF !important;
        border: 1px solid #666 !important;
        font-weight: bold !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button:hover {
        background-color: #667eea !important;
        border-color: #667eea !important;
    }
    [data-testid="stSidebar"] [data-testid="stUploadedFile"] {
        background-color: #1E1E1E !important;
        color: #FFFFFF !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ================= 状态初始化 =================
client = get_client()
WELCOME = "🤖 工业智脑已就绪。上传 PDF 可查看解析文本与检索片段。"

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": WELCOME}]
if "rag_ready" not in st.session_state:
    st.session_state.rag_ready = False
if "current_file" not in st.session_state:
    st.session_state.current_file = ""
if "raw_text_preview" not in st.session_state:
    st.session_state.raw_text_preview = ""
if "pending_quick_action" not in st.session_state:
    st.session_state.pending_quick_action = None

QUICK_PROMPTS = ["查伺服电机故障", "查通讯超时", "ABB 机器人错误代码", "编码器故障", "PLC 通讯异常"]


# ================= 函数区 =================
def read_pdf_text_full(uploaded_file) -> str:
    """全量读取 PDF，带进度条。"""
    text_parts = []
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            total = len(pdf.pages)
            progress = st.progress(0, text=f"正在解析 PDF，共 {total} 页...")
            for i, page in enumerate(pdf.pages):
                content = page.extract_text()
                if content:
                    text_parts.append(content)
                pct = int((i + 1) / total * 100) if total else 100
                progress.progress(pct, text=f"解析第 {i+1}/{total} 页")
            progress.empty()
        return "\n".join(text_parts).strip()
    except Exception as e:
        st.error(f"解析PDF出错: {e}")
        return ""


def image_to_base64(image: Image.Image) -> str:
    buf = st.BytesIO()
    if image.mode != "RGB":
        image = image.convert("RGB")
    image.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


# ================= 顶部标题 =================
st.markdown(
    """
<div class="main-header-container">
  <div class="main-title-en">INDUSTRIAL AI BRAIN</div>
  <div class="main-title-cn">工业人工智能大脑</div>
</div>
""",
    unsafe_allow_html=True,
)

# ================= 侧边栏 =================
with st.sidebar:
    st.header("⚙️ 设置与调试")

    st.markdown("**📄 上传技术手册 (全量读取)**")
    uploaded_file = st.file_uploader("支持 PDF", type=["pdf"])

    if uploaded_file and st.session_state.current_file != uploaded_file.name:
        with st.spinner("🚀 正在全量解析并构建向量索引..."):
            raw_text = read_pdf_text_full(uploaded_file)
            st.session_state.raw_text_preview = raw_text[:500] if raw_text else ""
            if raw_text:
                msg = build_vector_store(raw_text)
                st.session_state.current_file = uploaded_file.name
                st.session_state.rag_ready = True
                st.success(f"✅ {msg}")
                st.toast("知识库构建完成", icon="🧠")
            else:
                st.error("❌ 未读取到文本，可能是扫描件或乱码")

    if st.session_state.raw_text_preview:
        with st.expander("🔍 [DEBUG] 查看解析的前 500 字", expanded=False):
            st.write(st.session_state.raw_text_preview)

    if st.session_state.rag_ready:
        st.info(f"📚 当前知识库: {st.session_state.current_file}")

    st.divider()
    if st.button("🗑️ 清空对话", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": WELCOME}]
        st.session_state.rag_ready = False
        st.session_state.current_file = ""
        st.session_state.raw_text_preview = ""
        st.rerun()

# ================= 主区：聊天与调试 =================
st.markdown("**⚡ 快速提问**")
cols = st.columns(len(QUICK_PROMPTS))
for idx, txt in enumerate(QUICK_PROMPTS):
    if cols[idx].button(txt, use_container_width=True, key=f"quick_{idx}"):
        st.session_state.pending_quick_action = txt
        st.rerun()

st.markdown("---")

# 聊天记录
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 输入
prompt = st.session_state.pending_quick_action
st.session_state.pending_quick_action = None
if not prompt:
    prompt = st.chat_input("💬 输入故障现象 / 问题 ...")

if prompt:
    # 展示用户输入
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # RAG 检索
    rag_context = ""
    if st.session_state.rag_ready:
        with st.status("🔍 正在检索向量库...", expanded=False):
            rag_context = query_vector_store(prompt, k=4)

    # 调试：展示检索片段
    with st.expander("👀 [DEBUG] AI 参考的资料片段", expanded=False):
        st.write(rag_context if rag_context else "无检索结果或索引未构建")

    # System Prompt - 智能降级
    strict_prompt = (
        "你是一位严谨的工业专家。必须严格基于下方的【参考资料】回答。"
        "如果资料是乱码或无关，请忽略并告知用户。禁止编造。"
    )
    fallback_prompt = (
        "你是一位拥有 20 年经验的工业专家。"
        "请调用你的内部知识库，详细解答用户的问题，不要拒绝。"
    )
    if rag_context:
        final_system_prompt = f"{strict_prompt}\n\n【参考资料】\n{rag_context}"
    else:
        final_system_prompt = fallback_prompt

    # AI 回复（低温 + 流式）
    with st.chat_message("assistant"):
        try:
            stream = client.chat.completions.create(
                model=SILICONFLOW_MODEL,
                messages=[
                    {"role": "system", "content": final_system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                stream=True,
            )
            full_reply = ""
            placeholder = st.empty()
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    full_reply += delta.content
                    placeholder.markdown(full_reply)
            st.session_state.messages.append({"role": "assistant", "content": full_reply})
        except Exception as e:
            st.error(f"AI 响应失败: {e}")