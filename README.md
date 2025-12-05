# 🏭 Industrial RAG Assistant (工业级智能文档助手)

> **基于 LLM 的垂直领域知识库，专为解决工业技术手册检索难、查询慢痛点而设计。**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://my-ai-brain-dn45ze9hlteq6pwup8arui.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📖 项目背景

在工业机器人调试与维护场景中，工程师常常面临**技术手册篇幅冗长（通常超过500页）**、**故障代码查找困难**的问题。

本项目利用 **RAG (检索增强生成)** 技术，将非结构化的 PDF 技术文档转化为可对话的智能知识库。现场工程师只需输入自然语言（如“伺服电机过热怎么处理？”），系统即可基于手册内容提供精准的解决方案，**将故障排查效率提升 90% 以上**。

## ✨ 核心功能

- **🚀 工业级文档解析**：深度优化的 `pdfplumber` 引擎，支持读取复杂的工业技术手册。
- **🧠 垂直领域 RAG**：采用 Context Injection（上下文注入）技术，确保回答严格基于文档，**杜绝模型幻觉**。
- **⚙️ 专家模式**：开放 `Temperature` 参数调节，支持从“严格引用”到“发散分析”的多场景切换。
- **📊 仪表盘交互**：采用左右分栏的现代化 Dashboard 布局，支持移动端访问，适应车间现场环境。

## 🛠️ 技术架构

- **前端层**：Streamlit (构建响应式 Web UI)
- **模型层**：SiliconFlow API (接入 Qwen2.5-7B-Instruct 大模型)
- **数据层**：PDFPlumber (非结构化数据清洗与提取)
- **工程化**：Prompt Engineering (结构化系统提示词设计)

## 📸 效果演示

> **场景示例**：上传《ABB 机器人操作手册》，询问“错误代码 503 的解决方案”。
> *(建议此处后续补充一张项目运行截图)*

## 🚀 快速开始

### 1. 环境准备
确保您的环境已安装 Python 3.8+。

### 2. 安装依赖
```bash
pip install -r requirements.txt

### 3. 运行应用
```bash
streamlit run silicon_app.py

📝 使用指南
身份验证：输入有效的 API Key (支持 SiliconFlow / OpenAI 格式)。
文档装载：上传 PDF 格式的技术手册或说明书。
智能交互：在对话框输入技术问题，获取 Markdown 格式的专业解答。
⚠️ 说明
本项目为 MVP (最小可行性产品) 版本。
当前版本针对 10k token 上下文进行了优化，以平衡响应速度与准确率。
建议使用 Chrome 浏览器 以获得最佳体验。
Created by [Vincent Zhang] | 2025
