import streamlit as st
import os
import re
from typing import List
from openai import OpenAI

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

# === 推荐使用 BAAI/bge-m3，支持多语言且稳定 ===
EMBEDDING_MODEL = "BAAI/bge-m3" 
PERSIST_DIRECTORY = "./chroma_db_local"

def clean_text(text: str) -> str:
    """
    强力清洗文本，去除乱码和特殊符号
    """
    if not text: return ""
    # 1. 去除控制字符 (如 \x00)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    # 2. 合并多余空格和换行
    text = re.sub(r'\s+', ' ', text).strip()
    return text

class SiliconFlowEmbedding(Embeddings):
    def __init__(self):
        try:
            api_key = st.secrets["SILICONFLOW_API_KEY"]
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.siliconflow.cn/v1"
            )
        except Exception:
            st.error("⚠️ 未找到 SILICONFLOW_API_KEY")
            self.client = None

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not self.client: return []
        embeddings = []
        for text in texts:
            try:
                # 必须清洗文本，否则 API 会报错或返回垃圾
                cleaned = clean_text(text)
                if not cleaned: 
                    embeddings.append([0.0]*1024)
                    continue
                    
                response = self.client.embeddings.create(
                    model=EMBEDDING_MODEL,
                    input=cleaned
                )
                embeddings.append(response.data[0].embedding)
            except Exception as e:
                print(f"Embedding error: {e}")
                embeddings.append([0.0]*1024)
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        if not self.client: return []
        try:
            cleaned = clean_text(text)
            response = self.client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=cleaned
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Query error: {e}")
            return [0.0]*1024

def build_vector_store(text_content):
    if not text_content: return "⚠️ 内容为空"
    
    # 清洗全文
    clean_content = clean_text(text_content)
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
    docs = [Document(page_content=x) for x in text_splitter.split_text(clean_content)]
    
    try:
        embedding_function = SiliconFlowEmbedding()
        # 强制重置数据库 (防止旧的垃圾数据干扰)
        if os.path.exists(PERSIST_DIRECTORY):
            import shutil
            shutil.rmtree(PERSIST_DIRECTORY)
            
        Chroma.from_documents(
            documents=docs,
            embedding=embedding_function,
            persist_directory=PERSIST_DIRECTORY
        )
        return f"✅ 知识库重构完成！清洗并索引了 {len(docs)} 个片段。"
    except Exception as e:
        return f"❌ 构建失败: {str(e)}"

def query_vector_store(question, k=4):
    if not os.path.exists(PERSIST_DIRECTORY):
        return ""
    try:
        embedding_function = SiliconFlowEmbedding()
        db = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=embedding_function)
        docs = db.similarity_search(question, k=k)
        
        # 返回结果不仅包含文本，最好加上来源页码（如果未来支持）
        # 这里为了调试，直接返回纯文本
        return "\n\n".join([f"[片段{i+1}]: {doc.page_content}" for i, doc in enumerate(docs)])
    except Exception as e:
        print(f"搜索失败: {e}")
        return ""