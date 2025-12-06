# 🤖 工业机器人智能故障诊断系统 v2.0

> **基于 Streamlit 和大语言模型的工业级故障诊断应用，专为工业机器人维护工程师设计**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![Powered by SiliconFlow](https://img.shields.io/badge/Powered%20by-SiliconFlow-orange.svg)](https://siliconflow.cn/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📋 项目简介

**工业机器人智能故障诊断系统 v2.0** 是一款专为工业机器人（ABB、Kuka、Fanuc 等）维护工程师打造的智能诊断工具。系统集成了先进的视觉语言模型，支持通过文字描述或现场照片进行故障诊断，大幅提升故障排查效率，降低设备停机时间。

### 🎯 解决的核心问题

- **故障代码查找困难**：传统手册查找耗时，AI 秒级响应
- **现场诊断效率低**：支持拍照上传，AI 直接看图诊断
- **经验依赖性强**：内置 20 年维修专家知识，新手也能快速上手
- **安全风险高**：自动提醒操作风险，避免安全事故

---

## ✨ 核心功能 (v2.0 升级亮点)

### 🔍 1. 多模态视觉诊断
- **图片识别**：支持上传故障现场照片（报错代码、仪表盘、线缆破损等）
- **智能分析**：基于 **Qwen2-VL-72B** (720亿参数) 视觉语言模型，自动识别图片中的关键信息
- **精准诊断**：结合图片内容和文字描述，提供综合诊断方案

### 👨‍🔧 2. 专家级人设
- **20年经验专家**：内置资深维修专家 System Prompt
- **结构化输出**：严格按照以下格式输出
  - **故障分析**：简述可能的原因
  - **排查步骤**：分步骤列出检查点（如万用表测量哪里、检查哪根线缆）
  - **安全警告**：提示操作风险（如高压电、机械臂坠落风险）

### 🚀 3. 便捷操作
- **一键导出**：支持导出对话记录为 Markdown 或 Word 格式
- **一键重置**：快速清空对话历史，开始新诊断
- **移动端适配**：隐藏多余 Streamlit 元素，界面简洁美观
- **预设问题**：提供快速提问按钮，无需手动输入

### ⚡ 4. 高性能
- **流式输出**：采用 Streaming 技术，响应速度快，用户体验流畅
- **文档问答**：支持上传 PDF 技术手册，基于文档内容回答
- **上下文记忆**：保持对话上下文，支持多轮交互

---

## 🛠️ 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.10+ | 核心开发语言 |
| **Streamlit** | 1.28+ | Web 应用框架 |
| **OpenAI Client** | Latest | 调用硅基流动 API |
| **Pillow (PIL)** | 10.0+ | 图片处理 |
| **pdfplumber** | 0.9+ | PDF 文档解析 |
| **python-docx** | Latest | Word 文档导出（可选） |

### 🔌 API 服务

- **模型提供商**：SiliconFlow（硅基流动）
- **视觉模型**：Qwen/Qwen2-VL-72B-Instruct
- **API 格式**：OpenAI 兼容格式

---

## 🚀 快速开始

### 1. 环境准备

确保您的环境已安装 **Python 3.10+**。

```bash
python --version  # 检查 Python 版本
```

### 2. 克隆仓库

```bash
git clone <your-repo-url>
cd <your-repo-name>
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

**依赖列表：**
```
streamlit>=1.28.0
openai>=1.0.0
pdfplumber>=0.9.0
pillow>=10.0.0
python-docx>=1.0.0  # 可选，用于 Word 导出
```

### 4. 配置 API Key

创建 `.streamlit/secrets.toml` 文件（如果目录不存在，请先创建）：

```bash
mkdir -p .streamlit
```

在 `.streamlit/secrets.toml` 文件中添加您的硅基流动 API Key：

```toml
SILICONFLOW_API_KEY = "sk-your-actual-api-key-here"
```

> **💡 提示**：
> - 在 [SiliconFlow 官网](https://siliconflow.cn/) 注册并获取 API Key
> - 确保 API Key 以 `sk-` 开头
> - 不要将 `secrets.toml` 文件提交到版本控制系统

### 5. 运行应用

```bash
streamlit run silicon_app.py
```

应用将在浏览器中自动打开，默认地址：`http://localhost:8501`

---

## 📖 使用指南

### 基础使用

1. **直接提问**
   - 在聊天框输入故障现象描述
   - 例如："伺服电机报警，显示错误代码 503"

2. **上传图片诊断**
   - 点击上方 **⚙️ 设置** 按钮
   - 在侧边栏上传故障现场照片
   - 输入问题描述，AI 会结合图片内容进行诊断

3. **基于文档问答**
   - 在设置页面上传 PDF 技术手册
   - 系统会基于文档内容回答问题
   - 适合查找特定故障代码或操作步骤

### 高级功能

- **预设问题**：点击快速提问按钮，无需手动输入
- **导出对话**：点击下载按钮，保存诊断记录为 Markdown 或 Word
- **重置对话**：点击"开启新对话"按钮，清空历史记录

---

## 📸 功能演示

### 场景 1：文字描述诊断

**用户输入：**
```
伺服电机运行时发出异响，温度升高
```

**AI 输出：**
```
**故障分析**：可能原因包括轴承磨损、润滑不足或负载过大。

**排查步骤**：
1. 使用万用表测量电机电流，检查是否超载
2. 检查轴承润滑情况，必要时添加润滑脂
3. 检查机械连接，确认无松动或卡滞

**安全警告**：⚠️ 操作前务必断电，避免触电风险。高温时不要直接触摸电机外壳。
```

### 场景 2：图片诊断

上传包含错误代码的显示屏照片，AI 会自动识别错误代码并提供解决方案。

---

## ⚠️ 重要注意事项

### 🔒 安全提示

1. **AI 建议仅供参考**：本系统提供的诊断建议基于通用知识，实际故障可能因设备型号、使用环境等因素而异
2. **高压操作需谨慎**：涉及高压电、机械臂等危险操作时，请务必：
   - 断电操作
   - 佩戴防护设备
   - 由专业工程师执行
3. **复杂故障请咨询厂家**：对于严重故障或不确定的情况，建议联系设备厂家技术支持

### 📝 使用建议

- **详细描述**：提供越详细的故障现象，诊断越准确
- **上传清晰图片**：确保图片清晰，错误代码可见
- **结合文档**：上传技术手册可获得更精准的答案

### 🔧 技术限制

- **模型能力**：基于 Qwen2-VL-72B 模型，对复杂多步骤故障可能需要多轮交互
- **文档大小**：建议 PDF 文档不超过 50MB，单次处理约 8000 字符
- **网络要求**：需要稳定的网络连接访问 SiliconFlow API

---

## 📁 项目结构

```
.
├── silicon_app.py          # 主应用文件
├── requirements.txt        # Python 依赖
├── README.md              # 项目文档
└── .streamlit/
    └── secrets.toml       # API Key 配置（需自行创建）
```

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 👤 作者

**Vincent Zhang**

---

## 🙏 致谢

- [SiliconFlow](https://siliconflow.cn/) - 提供强大的视觉语言模型 API
- [Streamlit](https://streamlit.io/) - 优秀的 Python Web 应用框架
- [Qwen Team](https://github.com/QwenLM) - 开源优秀的视觉语言模型

---

**⭐ 如果这个项目对您有帮助，请给个 Star！**
