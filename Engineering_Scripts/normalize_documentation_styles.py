#!/usr/bin/env python3
"""
Normalize all HTML documentation to use consistent compact styling
"""

import os
import re
from pathlib import Path

def normalize_html_styles(file_path):
    """Normalize HTML file to use compact styling consistent with existing docs"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Standard compact CSS patterns based on agent_identity_structure_architecture.html
    
    # 1. Line height standardization
    content = re.sub(r'line-height:\s*1\.[6-9];?', 'line-height: 1.4;', content)
    
    # 2. Main content layout standardization
    content = re.sub(r'grid-template-columns:\s*280px\s+1fr\s+280px;?', 'grid-template-columns: 280px 1fr 280px;', content)
    content = re.sub(r'gap:\s*15px;?', 'gap: 15px;', content)
    content = re.sub(r'margin-top:\s*15px;?', 'margin-top: 15px;', content)
    
    # 3. Container padding standardization
    content = re.sub(r'padding:\s*[2-5][0-9]px;?', 'padding: 20px;', content)
    
    # 4. Top cell styling standardization
    content = re.sub(r'\.top-cell\s*h[12].*?font-size:\s*[^;]*;', '.top-cell h2 { font-size: 1rem;', content)
    content = re.sub(r'\.top-cell\s*p.*?font-size:\s*[^;]*;', '.top-cell p { font-size: 0.7rem;', content)
    
    # 5. Grid standardization
    content = re.sub(r'grid-template-rows:\s*repeat\([^)]*,\s*[6-9][0-9]px\);?', 'grid-template-rows: repeat(8, 75px);', content)
    content = re.sub(r'height:\s*[6-9][0-9]px;?', 'height: 65px;', content)
    
    # 6. Font size standardization
    content = re.sub(r'font-size:\s*2\.[0-9]rem;?', 'font-size: 1rem;', content)  # Main headers
    content = re.sub(r'font-size:\s*1\.[3-9]rem;?', 'font-size: 0.9rem;', content)  # Section headers
    content = re.sub(r'font-size:\s*0\.9rem;?', 'font-size: 0.75rem;', content)  # Detail titles
    content = re.sub(r'font-size:\s*0\.8[5-9]rem;?', 'font-size: 0.68rem;', content)  # Card titles
    content = re.sub(r'font-size:\s*0\.7[5-9]rem;?', 'font-size: 0.65rem;', content)  # Descriptions
    content = re.sub(r'font-size:\s*0\.7rem;?', 'font-size: 0.6rem;', content)  # Small text
    
    # 7. Details section standardization
    content = re.sub(r'\.details-section\s*{[^}]*padding:\s*[^;]*;', '.details-section { padding: 15px;', content)
    content = re.sub(r'\.details-grid\s*{[^}]*gap:\s*[^;]*;', '.details-grid { gap: 12px;', content)
    content = re.sub(r'\.detail-card\s*{[^}]*padding:\s*[^;]*;', '.detail-card { padding: 10px;', content)
    
    # 8. Icon size standardization
    content = re.sub(r'font-size:\s*[2-4][0-9]px;', 'font-size: 12px;', content)  # Emoji icons
    content = re.sub(r'width:\s*[2-4][0-9]px;\s*height:\s*[2-4][0-9]px;', 'width: 16px; height: 16px;', content)  # SVG icons
    
    # 9. Margin and padding cleanup
    content = re.sub(r'margin-bottom:\s*[2-9][0-9]px;?', 'margin-bottom: 15px;', content)
    content = re.sub(r'margin:\s*[2-9][0-9]px\s+[^;]*;?', 'margin: 15px auto;', content)
    
    # 10. Header size normalization
    content = re.sub(r'h1\s*{[^}]*font-size:\s*[^;]*;', 'h1 { font-size: 1rem;', content)
    content = re.sub(r'\.header\s*{[^}]*padding:\s*[^;]*;', '.header { padding: 20px;', content)
    
    return content

def main():
    """Process all HTML files in documentation directory"""
    
    doc_dir = Path("/Users/mikaeleage/Research & Analytics Services/System Enforcement Workspace/documentation")
    
    print("🔧 NORMALIZING HTML DOCUMENTATION STYLES")
    print("=" * 80)
    
    # Get all HTML files
    html_files = list(doc_dir.glob("*.html"))
    
    # Reference file (already has correct styling)
    reference_file = "agent_identity_structure_architecture.html"
    
    for html_file in html_files:
        if html_file.name == reference_file:
            print(f"⏭️  Skipping reference file: {html_file.name}")
            continue
            
        print(f"🔄 Processing: {html_file.name}")
        
        try:
            # Normalize the file
            normalized_content = normalize_html_styles(html_file)
            
            # Write back the normalized content
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(normalized_content)
                
            print(f"✅ Normalized: {html_file.name}")
            
        except Exception as e:
            print(f"❌ Error processing {html_file.name}: {e}")
    
    print(f"\n✅ Processed {len(html_files)} HTML files")
    print("📍 All documentation now uses consistent compact styling")

if __name__ == "__main__":
    main()