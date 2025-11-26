import json
import os
from openai import OpenAI

# ================= CONFIGURATION =================
# DeepSeek API Key
api_key = "sk-b103808f109b475983bcc90ce96ffb2a" 
# =================================================

def load_data():
    try:
        with open('schema.json', 'r', encoding='utf-8') as f:
            schema = json.load(f)
        with open('cleaned_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return schema, data
    except FileNotFoundError as e:
        print(f"错误: 找不到文件 - {e}")
        print("请检查 schema.json 和 cleaned_data.json 是否在当前文件夹里。")
        return None, None

def extract_triples(client, text, schema):
    system_prompt = f"""
You are an AGV (Automated Guided Vehicle) Safety Expert.
Your task is to extract knowledge triples from the provided text based on the following ontology schema:

Schema:
{json.dumps(schema, ensure_ascii=False, indent=2)}

Instructions:
1. Identify entities mentioned in the text that match the 'entities' types in the schema.
2. Identify relations between these entities that match the 'relations' types in the schema.
3. Output the result strictly in JSON format.
4. The JSON output should have two keys: "entities" and "relations".
   - "entities": A list of objects, each with "id" (unique name), "type", and "description" (optional, from text).
   - "relations": A list of objects, each with "source" (entity id), "target" (entity id), and "type".
5. If no entities or relations are found, return empty lists.

Input Text:
"""
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0,
            response_format={ "type": "json_object" }
        )
        
        result = response.choices[0].message.content
        return json.loads(result)
    except Exception as e:
        print(f"抽取过程中出错: {e}")
        return None

def main():
    # Initialize client with DeepSeek base URL
    client = OpenAI(
        api_key="sk-b103808f109b475983bcc90ce96ffb2a", 
        base_url="https://api.deepseek.com" 
    )
    
    schema, data = load_data()
    if not schema or not data:
        return

    print("成功加载 schema 和数据。")
    
    # Test with first 3 chunks
    # test_chunks = data[:3] 处理前三行数据
    chunks_to_process = data
    all_extracted_data = []

    print(f"正在处理前 {len(chunks_to_process)} 个文本块进行测试...")
    
    for i, chunk in enumerate(chunks_to_process):
        # Compatible with different key names (content or text)
        content = chunk.get('content') or chunk.get('text')
        section_id = chunk.get('section_id') or chunk.get('source') or "Unknown"

        if not content:
            print(f"跳过第 {i+1} 块，因为内容为空。")
            continue

        print(f"\n--- 正在处理第 {i+1} 块 (ID: {section_id}) ---")
        print(f"内容预览: {content[:50]}...")
        
        extracted = extract_triples(client, content, schema)
        
        if extracted:
            print("✅ 抽取成功:")
            # Print preview to avoid flooding
            print(json.dumps(extracted, ensure_ascii=False, indent=2)[:200] + "...")
            
            extracted['source_chunk_id'] = section_id
            all_extracted_data.append(extracted)
        else:
            print("❌ 抽取失败或结果为空。")

    # Save results
    output_file = "knowledge_graph.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_extracted_data, f, ensure_ascii=False, indent=2)
    print(f"\n测试完成！结果已保存到 {output_file}")

if __name__ == "__main__":
    main()
