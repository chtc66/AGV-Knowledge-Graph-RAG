from neo4j import GraphDatabase

# 配置
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "12345678")  # 确保密码正确

# 定义同义词字典 { "要被删除的名字": "保留的主名字" }
SYNONYMS = {
    "Lidar": "激光雷达",
    "LiDAR": "激光雷达",
    "激光扫描仪": "激光雷达",
    "AGV小车": "AGV",
    "自动导引车": "AGV",
    "急停": "急停按钮",
    "E-Stop": "急停按钮"
}

def merge_nodes(tx, bad_name, good_name):
    # 定义查询语句
    query = """
    MATCH (bad {name: $bad_name})
    WITH bad
    OPTIONAL MATCH (good {name: $good_name})
    WITH bad, good
    CALL apoc.do.case([
        good IS NOT NULL, 
        'CALL apoc.refactor.mergeNodes([good, bad], {properties:{name:"discard", description:"combine"}, mergeRels:true}) YIELD node RETURN node',
        good IS NULL,
        'SET bad.name = $good_name RETURN bad AS node'
    ], '', {bad:bad, good:good, good_name:$good_name})
    YIELD value
    RETURN value
    """
    
    # 执行查询 (注意这里缩进要对齐)
    try:
        result = tx.run(query, bad_name=bad_name, good_name=good_name)
        record = result.single()
        if record:
            print(f"✅ 已处理: {bad_name} -> {good_name}")
        else:
            print(f"⚠️ 未找到: {bad_name} (可能已处理或不存在)")
    except Exception as e:
        print(f"❌ 错误 ({bad_name}): {e}")

def main():
    driver = GraphDatabase.driver(URI, auth=AUTH)
    
    print("--- 开始实体对齐 ---")
    with driver.session() as session:
        # 1. 先检查 APOC 是否安装
        try:
            # 这里的 apoc.version 要加引号，是 Cypher 语句
            session.run("RETURN apoc.version()")
        except Exception as e:
            print(f"🚨 错误: APOC 插件检查失败。请确认插件已安装。\n报错详情: {e}")
            return

        # 2. 循环执行对齐
        for bad, good in SYNONYMS.items():
            session.execute_write(merge_nodes, bad, good)
            
    print("--- 对齐完成 ---")
    driver.close()

if __name__ == "__main__":
    main()