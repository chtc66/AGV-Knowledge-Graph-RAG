import pdfplumber
import json
import os
import re

def extract_text_from_pdf(pdf_path):
    sections = []
    current_section = {"section_id": "0", "content": ""}
    
    # Regex for section headers like "4.1", "4.2.1"
    # Assumes section starts at the beginning of a line
    section_pattern = re.compile(r'^\s*(\d+(\.\d+)+)\s+')
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                
                lines = text.split('\n')
                
                # Simple header/footer filtering based on line position or content
                # This is a heuristic: skip lines that are just numbers (page numbers)
                filtered_lines = []
                for line in lines:
                    if re.match(r'^\s*\d+\s*$', line): # Skip page numbers
                        continue
                    filtered_lines.append(line)
                
                for line in filtered_lines:
                    match = section_pattern.match(line)
                    if match:
                        # Save previous section if it has content
                        if current_section["content"].strip():
                            sections.append(current_section)
                        
                        # Start new section
                        section_id = match.group(1)
                        current_section = {
                            "section_id": section_id,
                            "content": line
                        }
                    else:
                        current_section["content"] += "\n" + line
            
            # Append the last section
            if current_section["content"].strip():
                sections.append(current_section)
                
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        
    return sections

def main():
    pdf_dir = os.path.join(os.getcwd(), "AGV pdf")
    output_file = "cleaned_data.json"
    all_data = []
    
    if not os.path.exists(pdf_dir):
        print(f"Directory not found: {pdf_dir}")
        return

    print(f"Scanning directory: {pdf_dir}")
    
    for filename in os.listdir(pdf_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(pdf_dir, filename)
            print(f"Processing: {filename}")
            file_sections = extract_text_from_pdf(pdf_path)
            
            # Add source file info to sections (optional but useful)
            for section in file_sections:
                section['source_file'] = filename
                
            all_data.extend(file_sections)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully processed {len(all_data)} sections.")
    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    main()
