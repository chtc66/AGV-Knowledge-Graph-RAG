from neo4j import GraphDatabase
import json
import time

# ================= CONFIGURATION =================
# Neo4j connection settings
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "12345678")
INPUT_FILE = "knowledge_graph.json"
# =================================================

def import_data(tx, data):
    # 1. Import Entities
    print("  Importing Entities...")
    count_entities = 0
    for chunk in data:
        if "entities" in chunk:
            for entity in chunk["entities"]:
                # Dynamic Label based on type (sanitize to avoid injection if needed, but assuming safe here)
                label = entity.get("type", "Thing").replace(" ", "_")
                entity_id = entity.get("id")
                
                if not entity_id:
                    continue

                # Cypher query using MERGE to avoid duplicates
                query = (
                    f"MERGE (n:`{label}` {{id: $id}}) "
                    "ON CREATE SET n.description = $description, n.name = $id "
                    "ON MATCH SET n.description = $description"
                )
                tx.run(query, id=entity_id, description=entity.get("description", ""))
                count_entities += 1
    print(f"  Processed {count_entities} entities.")

    # 2. Import Relations
    print("  Importing Relations...")
    count_relations = 0
    for chunk in data:
        if "relations" in chunk:
            for relation in chunk["relations"]:
                source_id = relation.get("source")
                target_id = relation.get("target")
                rel_type = relation.get("type", "RELATED_TO").replace(" ", "_").upper()
                
                if not source_id or not target_id:
                    continue

                # Cypher query to create relationship
                # Matches nodes by ID regardless of label (more flexible)
                query = (
                    "MATCH (a {id: $source_id}), (b {id: $target_id}) "
                    f"MERGE (a)-[r:`{rel_type}`]->(b) "
                )
                tx.run(query, source_id=source_id, target_id=target_id)
                count_relations += 1
    print(f"  Processed {count_relations} relations.")

def main():
    print(f"Reading data from {INPUT_FILE}...")
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Loaded {len(data)} chunks of data.")
    except FileNotFoundError:
        print(f"Error: File {INPUT_FILE} not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from {INPUT_FILE}.")
        return

    print(f"Connecting to Neo4j at {URI}...")
    driver = None
    try:
        driver = GraphDatabase.driver(URI, auth=AUTH)
        driver.verify_connectivity()
        print("Connected successfully!")
        
        with driver.session() as session:
            session.execute_write(import_data, data)
            
        print("\nImport completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error connecting to Neo4j or importing data: {e}")
        print("Tip: Make sure your Neo4j container is running and port 7687 is exposed.")
        print("You can check with: docker ps")
    finally:
        if driver:
            driver.close()

if __name__ == "__main__":
    main()
