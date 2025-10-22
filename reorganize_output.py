#!/usr/bin/env python3
"""
Reorganize existing JSON files into year/month subdirectories
"""

import os
import json
import shutil
from datetime import datetime


def reorganize_files(output_dir="output"):
    """Reorganize flat JSON files into year/month subdirectories"""
    
    # Find all JSON files in the root of output directory
    json_files = [f for f in os.listdir(output_dir) 
                  if f.endswith('.json') and os.path.isfile(os.path.join(output_dir, f))]
    
    if not json_files:
        print("No JSON files found in output directory root.")
        return
    
    print(f"Found {len(json_files)} files to reorganize...")
    moved = 0
    skipped = 0
    
    for filename in json_files:
        old_path = os.path.join(output_dir, filename)
        
        try:
            # Read the JSON file to get the air_date
            with open(old_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            air_date = data.get('air_date')
            if not air_date:
                print(f"  ⚠ Skipping {filename} - no air_date found")
                skipped += 1
                continue
            
            # Parse the date
            date_obj = datetime.strptime(air_date, "%A, %B %d, %Y")
            year = str(date_obj.year)
            month = f"{date_obj.month:02d}"
            
            # Create new directory structure
            new_dir = os.path.join(output_dir, year, month)
            os.makedirs(new_dir, exist_ok=True)
            
            # Move the file
            new_path = os.path.join(new_dir, filename)
            
            if os.path.exists(new_path):
                # File already exists - compare and keep newer or delete duplicate
                shutil.move(old_path, new_path.replace('.json', '_dup.json'))
                print(f"  ⚠ Duplicate {filename} - saved as *_dup.json in {year}/{month}/")
                moved += 1
            else:
                shutil.move(old_path, new_path)
                print(f"  ✓ Moved {filename} → {year}/{month}/")
                moved += 1
                
        except (ValueError, json.JSONDecodeError, KeyError) as e:
            print(f"  ✗ Error processing {filename}: {e}")
            skipped += 1
    
    print(f"\n{'='*60}")
    print(f"Reorganization complete!")
    print(f"✓ Moved: {moved} files")
    if skipped > 0:
        print(f"⚠ Skipped: {skipped} files")
    print(f"{'='*60}")


if __name__ == "__main__":
    reorganize_files()

