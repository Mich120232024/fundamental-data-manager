#!/usr/bin/env python3
"""
Analyze the ACTUAL Research Library files
"""

import glob
import os
from collections import defaultdict

def analyze_actual_library():
    library_path = "/Users/mikaeleage/Institutional Data Center/Research Library"
    
    print("=== ACTUAL Research Library Analysis ===")
    print(f"Source: {library_path}")
    print()
    
    # Find all .md files in the Research Library
    pattern = f"{library_path}/**/*.md"
    files = glob.glob(pattern, recursive=True)
    
    print(f"Total .md files found: {len(files)}")
    print()
    
    # Analyze by size and directory
    files_by_size = defaultdict(list)
    files_by_directory = defaultdict(list)
    
    for file_path in files:
        try:
            size = os.path.getsize(file_path)
            
            # Size categories
            if size < 1000:
                category = "tiny (<1KB)"
            elif size < 10000:
                category = "small (1-10KB)"
            elif size < 100000:
                category = "medium (10-100KB)"
            elif size < 1000000:
                category = "large (100KB-1MB)"
            else:
                category = "huge (>1MB)"
            
            files_by_size[category].append((file_path, size))
            
            # Directory categories
            rel_path = os.path.relpath(file_path, library_path)
            dir_name = rel_path.split('/')[0] if '/' in rel_path else 'Root'
            files_by_directory[dir_name].append((file_path, size))
            
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    print("📊 SIZE DISTRIBUTION:")
    total_migrable = 0
    for category, files in files_by_size.items():
        print(f"{category}: {len(files)} files")
        if "huge" not in category:
            total_migrable += len(files)
    
    print(f"\n✅ Potentially migrable: {total_migrable} files")
    print(f"❌ Too large (>1MB): {len(files_by_size.get('huge (>1MB)', []))} files")
    
    print("\n📂 DIRECTORY DISTRIBUTION:")
    for dir_name, files in sorted(files_by_directory.items()):
        total_size = sum(size for _, size in files)
        print(f"{dir_name}: {len(files)} files ({total_size:,} bytes)")
    
    # Show some sample files from each directory
    print("\n📋 SAMPLE FILES BY DIRECTORY:")
    for dir_name, files in sorted(files_by_directory.items()):
        if files:
            sample_files = files[:3]  # First 3 files
            print(f"\n{dir_name}:")
            for file_path, size in sample_files:
                filename = os.path.basename(file_path)
                print(f"  - {filename} ({size:,} bytes)")
    
    # Show large files if any
    if "huge (>1MB)" in files_by_size:
        print("\n⚠️  LARGE FILES THAT NEED SPECIAL HANDLING:")
        for file_path, size in files_by_size["huge (>1MB)"]:
            rel_path = os.path.relpath(file_path, library_path)
            print(f"  {size:,} bytes: {rel_path}")

if __name__ == "__main__":
    analyze_actual_library()