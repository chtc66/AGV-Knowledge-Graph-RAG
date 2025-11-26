from neo4j import GraphDatabase

# 配置连接
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "12345678") # 记得改你的密码

driver = GraphDatabase.driver(URI, auth=AUTH)

def run_query(tx, query):
    result = tx.run(query)
    # 打印被删除的数量
    summary = result.consume()
    print(f"执行语句: {query[:50]}...")
    print(f"Deleted nodes: {summary.counters.nodes_deleted}")
    print(f"Deleted relationships: {summary.counters.relationships_deleted}")

def clean_data():
    queries = [
        # 1. 删除没有名字的节点
        """
        MATCH (n) 
        WHERE n.name IS NULL OR n.name = "" OR n.name = "N/A"
        DETACH DELETE n
        """,
        # 2. 删除属性极少的无效节点 (假设正常节点至少有 id, name, type 3个属性，这里阈值设为1或2根据实际情况定)
        """
        MATCH (n) 
        WHERE size(keys(n)) <= 1 
        DETACH DELETE n
        """,
        # 3. (可选) 删除完全孤立的 Component 类型的节点
        """
        MATCH (n:Component) 
        WHERE NOT (n)--() 
        DETACH DELETE n
        """
    ]

    with driver.session() as session:
        print("--- 开始自动化清洗图谱 ---")
        for q in queries:
            session.execute_write(run_query, q)
        print("--- 清洗完成 ---")

if __name__ == "__main__":
    clean_data()
    driver.close()