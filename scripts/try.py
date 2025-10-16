import os
import re
from pathlib import Path

def rename_folders_with_prefix_sequential(directory_path, prefix_pattern='t', dry_run=True):
    """
    Rename folders with prefix and numbers to sequential numbers starting from 0
    Handles non-consecutive numbers (e.g., t001, t002, t005, t010)
    
    Args:
        directory_path: Path to the directory containing folders to rename
        prefix_pattern: Prefix pattern to match (default: 't')
        dry_run: If True, only preview changes without actually renaming
    
    Examples:
        't001' -> '0'
        't002' -> '1'
        't005' -> '2' (note: skipped t003, t004)
        't010' -> '3'
    """
    # Check if directory exists
    if not os.path.exists(directory_path):
        print(f"Error: Directory not found: {directory_path}")
        return
    
    # Get all items in directory
    items = os.listdir(directory_path)
    folders = [item for item in items if os.path.isdir(os.path.join(directory_path, item))]
    
    if not folders:
        print("No folders found in the directory.")
        return
    
    print(f"Found {len(folders)} folders")
    print(f"Pattern: {prefix_pattern}[number] -> sequential numbers from 0")
    print("="*60)
    
    # Parse folder names and extract numbers
    parsed_folders = []
    skipped_folders = []
    
    # Pattern: prefix followed by digits
    pattern = rf'^{re.escape(prefix_pattern)}(\d+)$'
    
    for folder_name in folders:
        match = re.match(pattern, folder_name)
        if match:
            number = int(match.group(1))
            parsed_folders.append((folder_name, number))
        else:
            print(f"Skipping '{folder_name}' (doesn't match pattern '{prefix_pattern}[number]')")
            skipped_folders.append(folder_name)
    
    if not parsed_folders:
        print(f"No folders matching the pattern '{prefix_pattern}[number]' found.")
        return
    
    # Sort by the original number
    parsed_folders.sort(key=lambda x: x[1])
    
    # Display original numbering analysis
    print("\nOriginal Numbering Analysis:")
    print("-"*60)
    original_numbers = [num for _, num in parsed_folders]
    print(f"Total folders: {len(parsed_folders)}")
    print(f"Original number range: {min(original_numbers)} to {max(original_numbers)}")
    
    # Check for gaps
    expected_range = set(range(min(original_numbers), max(original_numbers) + 1))
    actual_numbers = set(original_numbers)
    missing_numbers = expected_range - actual_numbers
    
    if missing_numbers:
        print(f"Non-consecutive: Missing {len(missing_numbers)} numbers")
        if len(missing_numbers) <= 20:
            print(f"  Missing numbers: {sorted(missing_numbers)}")
        else:
            print(f"  Missing numbers (first 20): {sorted(missing_numbers)[:20]}")
            print(f"  ... and {len(missing_numbers) - 20} more")
    else:
        print("All numbers are consecutive")
    
    print("-"*60)
    
    # Create mapping to sequential IDs
    folder_mapping = []
    temp_mapping = []
    
    for new_id, (folder_name, original_number) in enumerate(parsed_folders):
        old_path = os.path.join(directory_path, folder_name)
        new_name = str(new_id)
        new_path = os.path.join(directory_path, new_name)
        
        # Temporary name for two-phase renaming
        temp_name = f"TEMP_{new_id:05d}"
        temp_path = os.path.join(directory_path, temp_name)
        
        folder_mapping.append((old_path, new_path, folder_name, new_name, new_id, original_number))
        temp_mapping.append((old_path, temp_path, new_path, folder_name, temp_name, new_name))
    
    # Display preview
    print(f"\nRename Preview:")
    print("-"*60)
    
    # Show first 15 mappings
    for old_path, new_path, old_name, new_name, new_id, orig_num in folder_mapping[:15]:
        print(f"  '{old_name}' (orig_num={orig_num:03d}) -> '{new_name}'")
    
    if len(folder_mapping) > 15:
        print(f"  ...")
        # Show last few
        for old_path, new_path, old_name, new_name, new_id, orig_num in folder_mapping[-5:]:
            print(f"  '{old_name}' (orig_num={orig_num:03d}) -> '{new_name}'")
    
    print("-"*60)
    print(f"Total: {len(folder_mapping)} folders to rename")
    print(f"New ID range: 0 to {len(folder_mapping) - 1}")
    
    if skipped_folders:
        print(f"\nSkipped: {len(skipped_folders)} folders")
        for folder in skipped_folders[:10]:
            print(f"  - {folder}")
        if len(skipped_folders) > 10:
            print(f"  ... and {len(skipped_folders) - 10} more")
    
    # Perform renaming
    if dry_run:
        print("\n[DRY RUN MODE] No changes made.")
        print("Set dry_run=False to perform actual renaming.")
        print("\nNote: Using two-phase renaming with temporary names to avoid conflicts.")
    else:
        print("\nPerforming renaming using two-phase approach...")
        print("Phase 1: Rename to temporary names...")
        
        # Phase 1: Rename all to temporary names
        phase1_success = 0
        phase1_failed = 0
        successful_temps = []
        
        for old_path, temp_path, new_path, old_name, temp_name, new_name in temp_mapping:
            try:
                os.rename(old_path, temp_path)
                if phase1_success < 10 or phase1_success % 20 == 0:
                    print(f"   '{old_name}' -> '{temp_name}'")
                successful_temps.append((temp_path, new_path, temp_name, new_name, old_name))
                phase1_success += 1
            except Exception as e:
                print(f"   Failed to rename '{old_name}' to temp: {e}")
                phase1_failed += 1
        
        if phase1_success > 10:
            print(f"  ... (showing sample progress, {phase1_success} total)")
        
        print(f"\nPhase 1 complete: {phase1_success} success, {phase1_failed} failed")
        
        if phase1_failed > 0:
            print("\nError in Phase 1. Rolling back...")
            # Rollback
            for temp_path, new_path, temp_name, new_name, old_name in successful_temps:
                old_path = os.path.join(directory_path, old_name)
                try:
                    os.rename(temp_path, old_path)
                    print(f"  Rolled back: '{temp_name}' -> '{old_name}'")
                except Exception as e:
                    print(f"  Failed to rollback '{temp_name}': {e}")
            return
        
        # Phase 2: Rename from temporary names to final names
        print("\nPhase 2: Rename to final names...")
        phase2_success = 0
        phase2_failed = 0
        
        for temp_path, new_path, temp_name, new_name, old_name in successful_temps:
            try:
                os.rename(temp_path, new_path)
                if phase2_success < 10 or phase2_success % 20 == 0:
                    print(f"   '{temp_name}' -> '{new_name}'")
                phase2_success += 1
            except Exception as e:
                print(f"   Failed to rename '{temp_name}' to '{new_name}': {e}")
                phase2_failed += 1
        
        if phase2_success > 10:
            print(f"  ... (showing sample progress, {phase2_success} total)")
        
        print("\n" + "="*60)
        print("Renaming Complete!")
        print("="*60)
        print(f"Phase 1 (to temp): {phase1_success} success, {phase1_failed} failed")
        print(f"Phase 2 (to final): {phase2_success} success, {phase2_failed} failed")
        print(f"Total successfully renamed: {phase2_success} folders")


def analyze_prefix_number_folders(directory_path, prefix_pattern='t'):
    """
    Analyze folders with prefix and number pattern
    
    Args:
        directory_path: Path to the directory to analyze
        prefix_pattern: Prefix pattern to match (default: 't')
    """
    if not os.path.exists(directory_path):
        print(f"Error: Directory not found: {directory_path}")
        return
    
    items = os.listdir(directory_path)
    folders = [item for item in items if os.path.isdir(os.path.join(directory_path, item))]
    
    if not folders:
        print("No folders found.")
        return
    
    print("="*60)
    print("Folder Pattern Analysis")
    print("="*60)
    print(f"Total folders: {len(folders)}")
    print(f"Looking for pattern: {prefix_pattern}[number]")
    print()
    
    # Parse folders
    pattern = rf'^{re.escape(prefix_pattern)}(\d+)$'
    matching_folders = []
    non_matching = []
    
    for folder in folders:
        match = re.match(pattern, folder)
        if match:
            number = int(match.group(1))
            matching_folders.append((folder, number))
        else:
            non_matching.append(folder)
    
    if matching_folders:
        matching_folders.sort(key=lambda x: x[1])
        print(f"Matching folders: {len(matching_folders)}")
        print("-"*60)
        
        numbers = [num for _, num in matching_folders]
        print(f"Number range: {min(numbers)} to {max(numbers)}")
        
        # Check for gaps
        expected_range = set(range(min(numbers), max(numbers) + 1))
        actual_numbers = set(numbers)
        missing = expected_range - actual_numbers
        
        if missing:
            print(f"\nNon-consecutive numbering detected:")
            print(f"  Expected range: {min(numbers)} to {max(numbers)} ({len(expected_range)} numbers)")
            print(f"  Actual folders: {len(matching_folders)}")
            print(f"  Missing: {len(missing)} numbers")
            
            if len(missing) <= 30:
                print(f"  Missing numbers: {sorted(missing)}")
            else:
                print(f"  Missing numbers (first 30): {sorted(missing)[:30]}")
                print(f"  ... and {len(missing) - 30} more")
        else:
            print("\n All numbers are consecutive")
        
        # Show distribution
        print(f"\nFolder distribution:")
        print(f"  First 10 folders:")
        for folder, num in matching_folders[:10]:
            print(f"    {folder} (number={num})")
        
        if len(matching_folders) > 20:
            print(f"  ...")
            print(f"  Last 10 folders:")
            for folder, num in matching_folders[-10:]:
                print(f"    {folder} (number={num})")
        elif len(matching_folders) > 10:
            print(f"  Remaining folders:")
            for folder, num in matching_folders[10:]:
                print(f"    {folder} (number={num})")
        
        # Show sequential mapping preview
        print(f"\n\nSequential Mapping Preview (after renaming):")
        print("-"*60)
        print("Original -> New ID")
        for new_id, (folder, orig_num) in enumerate(matching_folders[:15]):
            print(f"  {folder} (orig={orig_num}) -> {new_id}")
        if len(matching_folders) > 15:
            print(f"  ... ({len(matching_folders) - 15} more)")
            print(f"  Final range will be: 0 to {len(matching_folders) - 1}")
    
    if non_matching:
        print(f"\n\nNon-matching folders: {len(non_matching)}")
        print("-"*60)
        for folder in non_matching[:10]:
            print(f"  - {folder}")
        if len(non_matching) > 10:
            print(f"  ... and {len(non_matching) - 10} more")


def save_prefix_number_mapping(directory_path, prefix_pattern='t', output_file="folder_mapping.txt"):
    """
    Save the folder mapping to a text file
    
    Args:
        directory_path: Path to the directory
        prefix_pattern: Prefix pattern to match
        output_file: Output file name
    """
    items = os.listdir(directory_path)
    folders = [item for item in items if os.path.isdir(os.path.join(directory_path, item))]
    
    # Parse and sort
    pattern = rf'^{re.escape(prefix_pattern)}(\d+)$'
    parsed_folders = []
    
    for folder_name in folders:
        match = re.match(pattern, folder_name)
        if match:
            number = int(match.group(1))
            parsed_folders.append((folder_name, number))
    
    parsed_folders.sort(key=lambda x: x[1])
    
    # Write to file
    output_path = os.path.join(directory_path, output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"Folder Mapping (prefix: '{prefix_pattern}')\n")
        f.write("="*60 + "\n")
        f.write("Original Folder Name -> New ID (Original Number)\n")
        f.write("-"*60 + "\n")
        
        for new_id, (folder_name, original_number) in enumerate(parsed_folders):
            f.write(f"{folder_name} -> {new_id} (orig_num={original_number})\n")
        
        f.write("\n" + "="*60 + "\n")
        f.write(f"Total folders: {len(parsed_folders)}\n")
        f.write(f"New ID range: 0 to {len(parsed_folders) - 1}\n")
    
    print(f"\nMapping saved to: {output_path}")


if __name__ == "__main__":
    # ==========================================
    # Rename folders with prefix and numbers
    # ==========================================
    directory_path = r"F:\archive\organized_by_identity"
    prefix = 't'  # Change this to match your prefix
    
    print("="*60)
    print("Folder Renaming: PREFIX[number] -> Sequential (0, 1, 2, ...)")
    print("="*60)
    print(f"Directory: {directory_path}")
    print(f"Prefix pattern: '{prefix}'")
    print(f"Handles non-consecutive numbers")
    print("="*60)
    print()
    
    # Step 0: Analyze folder structure (recommended)
    print("STEP 0: ANALYZE FOLDER STRUCTURE")
    print("="*60)
    analyze_prefix_number_folders(directory_path, prefix_pattern=prefix)
    
    # Step 1: Preview renaming
    print("\n\nSTEP 1: PREVIEW MODE")
    print("="*60)
    rename_folders_with_prefix_sequential(directory_path, prefix_pattern=prefix, dry_run=True)
    
    # Step 2: Save mapping to file (recommended)
    save_prefix_number_mapping(directory_path, prefix_pattern=prefix)
    
    # Step 3: Uncomment below to perform actual renaming
    # print("\n\nSTEP 3: ACTUAL RENAMING")
    # print("="*60)
    rename_folders_with_prefix_sequential(directory_path, prefix_pattern=prefix, dry_run=False)