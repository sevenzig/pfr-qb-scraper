#!/usr/bin/env python3
"""Fix syntax errors in splits_extractor.py by removing corrupted section"""

def fix_splits_extractor():
    file_path = r"src\scrapers\splits_extractor.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the corrupted method definition starting at line 951 (0-indexed: 950)
    # and remove everything until the good method definition at line 1325 (0-indexed: 1324)
    
    # Keep lines 0-949 (up to but not including line 950)
    good_lines = lines[:950]
    
    # Skip corrupted section (lines 950-1323) and keep from line 1324 onward
    good_lines.extend(lines[1324:])
    
    # Write the fixed file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(good_lines)
    
    print("Fixed splits_extractor.py by removing corrupted method definition")

if __name__ == "__main__":
    fix_splits_extractor()