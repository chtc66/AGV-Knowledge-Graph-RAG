import json
from neo4j import GraphDatabase
from openai import OpenAI

# ---------------- 配置区 ----------------
# 1. 填入你的 DeepSeek Key
api_key = "sk-b103808f109b475983bcc90ce96ffb2a" 
base_url = "https://api.deepseek.com"

# 2. 数据库配置
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "12345678")
# ----------------------------------------

def get_isolated_components(tx):
    """找出没有 MITIGATES 关系的部件"""
    query = """
    MATCH (c:Component)
    WHERE NOT (c)-[:MITIGATES]->(:Hazard)
    RETURN c.name AS name
    LIMIT 20
    """
    result = tx.run(query)
    return [record["name"] for record in result]

def add_relation(tx, comp_name, hazard_name):
    """写入关系：Component -> MITIGATES -> Hazard"""
    query = """
    MATCH (c:Component {name: $comp_name})
    MERGE (h:Hazard {name: $hazard_name})
    MERGE (c)-[:MITIGATES]->(h)
    """
    tx.run(query, comp_name=comp_name, hazard_name=hazard_name)
    print(f"🔗 已连接: {comp_name} --(抑制)--> {hazard_name}")

def ask_llm_for_hazards(client, component_name):
    """问 LLM 这个部件解决什么问题"""
    prompt = f"""
    在 AGV (移动机器人) 安全标准领域，部件 "{component_name}" 主要用于防止或抑制哪些具体的安全风险(Hazard)？
    
    请只返回最核心的 1-2 个风险名称。
    如果不清楚或该部件不直接涉及安全，请返回 "None"。
    
    格式要求：请仅返回 JSON 格式，不要 Markdown 标记。
    格式示例：{{"hazards": ["碰撞", "挤压"]}}
    """
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" },
            temperature=0.1
        )
        content = response.choices[0].message.content
        return json.loads(content).get("hazards", [])
    except Exception as e:
        print(f"LLM 调用失败: {e}")
        return []

def main():
    client = OpenAI(api_key=api_key, base_url=base_url)
    driver = GraphDatabase.driver(URI, auth=AUTH)
    
    with driver.session() as session:
        # 1. 获取孤立节点
        isolated_comps = session.execute_read(get_isolated_components)
        print(f"🔍 发现 {len(isolated_comps)} 个孤立部件需要补全关系...")
        
        # 2. 循环处理
        for comp in isolated_comps:
            print(f"\n正在分析部件: [{comp}] ...")
            
            # 问 AI
            hazards = ask_llm_for_hazards(client, comp)
            
            if not hazards or hazards == "None":
                print(f"⚠️ AI 认为 [{comp}] 不直接对应特定风险，跳过。")
                continue
            
            # 写回数据库
            for h in hazards:
                session.execute_write(add_relation, comp, h)
                
    driver.close()
    print("\n✅ 关系补全任务完成！")

if __name__ == "__main__":
    main()