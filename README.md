# 🤖 AGV Safety Knowledge Graph & RAG System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Neo4j](https://img.shields.io/badge/Neo4j-5.26-green)
![LangChain](https://img.shields.io/badge/LangChain-Integration-orange)
![状态](https://img.shields.io/badge/Status-Phase_2_Completed-success)

> 基于大模型 (LLM) 与知识图谱技术的 AGV 移动机器人安全标准问答系统。将非结构化 PDF 标准转化为结构化知识，实现智能检索与推理。

## 📸 Project Showcase (项目展示)

### 1. Neo4j 图谱可视化
<img width="2420" height="702" alt="68075a5f-c043-4184-98e2-d8e006ceb9ca" src="https://github.com/user-attachments/assets/91e9d328-061e-49d5-8874-0dc304e004a7" />

![Knowledge Graph Visualization](./assets/graph_preview.png)

### 2. 实体对齐效果
*(此处放一张 Lidar 和 激光雷达 被合并后的局部图，或者清洗脚本运行成功的终端截图)*
![Entity Resolution](./assets/cleaning_process.png)

## 📖 Background (项目背景)

工业安全标准（如 ISO 3691-4）通常以长篇幅 PDF 形式存在，查阅困难且难以进行自动化关联分析。本项目旨在：
1.  **结构化**：利用 LLM 提取标准中的实体（部件、风险、要求）及关系。
2.  **知识化**：构建 Neo4j 图谱，实现多跳推理（如：查找某部件潜在的所有风险）。
3.  **智能化**：(Phase 3) 结合 RAG 技术，提供基于事实依据的智能问答。

## 🛠️ Tech Stack (技术栈)

*   **Core**: Python, LangChain
*   **Database**: Neo4j (Graph), ChromaDB (Vector - Coming Soon)
*   **LLM Integration**: OpenAI / DeepSeek API
*   **ETL Pipeline**:
    *   `PDF Parsing`: pdfplumber
    *   `Extraction`: LLM-based Triple Extraction
    *   `Cleaning`: Neo4j APOC (Entity Resolution)

## 📂 Project Structure (目录结构)

```text
AGV-Knowledge-Graph/
├── schema.json              # 本体定义 (Ontology)
├── 1_parse_pdf.py           # PDF 解析与分块
├── 2_extract_triples.py     # LLM 三元组抽取 (Core)
├── 3_import_neo4j.py        # Neo4j 入库脚本
├── 4_clean_merge.py         # 实体对齐与清洗 (APOC)
├── 5_enrich_relations.py    # 关系补全
├── cleaned_data.json        # 中间处理数据
└── README.md                # 项目文档
