import os
import re
from pathlib import Path
import tempfile
import shutil

def rename_folders_decrement_safe(directory_path, dry_run=True):
    """
    Safely rename all numeric folders by subtracting 1 from their current number
    Uses temporary names to avoid conflicts
    
    Args:
        directory_path: Path to the directory containing folders to rename
        dry_run: If True, only preview changes without actually renaming
    
    Examples:
        '1' -> '0'
        '2' -> '1'
        '10' -> '9'
        '90' -> '89'
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
    print("Operation: Subtract 1 from each folder number (1-based -> 0-based)")
    print("="*60)
    
    # Store rename operations
    rename_operations = []
    skipped_folders = []
    
    for folder_name in folders:
        old_path = os.path.join(directory_path, folder_name)
        
        # Check if folder name is purely numeric
        if not folder_name.isdigit():
            print(f"Skipping '{folder_name}' (not a pure number)")
            skipped_folders.append(folder_name)
            continue
        
        # Convert to integer
        current_number = int(folder_name)
        
        # Subtract 1
        new_number = current_number - 1
        
        # Check if result is negative
        if new_number < 0:
            print(f"Warning: '{folder_name}' would become {new_number} (negative), skipping")
            skipped_folders.append(folder_name)
            continue
        
        new_name = str(new_number)
        new_path = os.path.join(directory_path, new_name)
        
        rename_operations.append((old_path, new_path, folder_name, new_name, current_number, new_number))
    
    # Sort by current number (ASCENDING) for proper renaming order
    rename_operations.sort(key=lambda x: x[4])
    
    # Display preview
    if rename_operations:
        print("\nRename Preview (sorted by current number, ascending):")
        print("-"*60)
        for old_path, new_path, old_name, new_name, curr_num, new_num in rename_operations[:20]:
            print(f"  '{old_name}' (ID={curr_num}) -> '{new_name}' (ID={new_num})")
        if len(rename_operations) > 20:
            print(f"  ... and {len(rename_operations) - 20} more")
        print("-"*60)
        print(f"Total: {len(rename_operations)} folders to rename")
        
        if skipped_folders:
            print(f"\nSkipped: {len(skipped_folders)} folders")
            for folder in skipped_folders[:10]:
                print(f"  - {folder}")
            if len(skipped_folders) > 10:
                print(f"  ... and {len(skipped_folders) - 10} more")
    else:
        print("No folders to rename.")
        if skipped_folders:
            print(f"\nAll {len(skipped_folders)} folders were skipped.")
        return
    
    # Perform renaming
    if dry_run:
        print("\n[DRY RUN MODE] No changes made.")
        print("Set dry_run=False to perform actual renaming.")
        print("\nNote: Using two-phase renaming with temporary names to avoid conflicts.")
    else:
        print("\nPerforming renaming using two-phase approach...")
        print("Phase 1: Rename to temporary names...")
        
        # Phase 1: Rename all to temporary names
        temp_mapping = []
        phase1_success = 0
        phase1_failed = 0
        
        for old_path, new_path, old_name, new_name, curr_num, new_num in rename_operations:
            # Create temporary name (prefix with 'TEMP_')
            temp_name = f"TEMP_{old_name}"
            temp_path = os.path.join(directory_path, temp_name)
            
            try:
                os.rename(old_path, temp_path)
                print(f"   '{old_name}' -> '{temp_name}'")
                temp_mapping.append((temp_path, new_path, temp_name, new_name))
                phase1_success += 1
            except Exception as e:
                print(f"   Failed to rename '{old_name}' to temp: {e}")
                phase1_failed += 1
        
        print(f"\nPhase 1 complete: {phase1_success} success, {phase1_failed} failed")
        
        if phase1_failed > 0:
            print("\nError in Phase 1. Rolling back...")
            # Rollback: rename temp names back to original
            for temp_path, new_path, temp_name, new_name in temp_mapping:
                original_name = temp_name.replace("TEMP_", "")
                original_path = os.path.join(directory_path, original_name)
                try:
                    os.rename(temp_path, original_path)
                    print(f"  Rolled back: '{temp_name}' -> '{original_name}'")
                except Exception as e:
                    print(f"  Failed to rollback '{temp_name}': {e}")
            return
        
        # Phase 2: Rename from temporary names to final names
        print("\nPhase 2: Rename to final names...")
        phase2_success = 0
        phase2_failed = 0
        
        for temp_path, new_path, temp_name, new_name in temp_mapping:
            try:
                os.rename(temp_path, new_path)
                print(f"   '{temp_name}' -> '{new_name}'")
                phase2_success += 1
            except Exception as e:
                print(f"   Failed to rename '{temp_name}' to '{new_name}': {e}")
                phase2_failed += 1
        
        print("\n" + "="*60)
        print("Renaming Complete!")
        print("="*60)
        print(f"Phase 1 (to temp): {phase1_success} success, {phase1_failed} failed")
        print(f"Phase 2 (to final): {phase2_success} success, {phase2_failed} failed")
        print(f"Total successfully renamed: {phase2_success} folders")


def analyze_numeric_folders(directory_path):
    """
    Analyze numeric folders in the directory
    
    Args:
        directory_path: Path to the directory to analyze
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
    print("Numeric Folder Analysis")
    print("="*60)
    print(f"Total folders: {len(folders)}")
    print()
    
    # Separate numeric and non-numeric folders
    numeric_folders = []
    non_numeric_folders = []
    
    for folder in folders:
        if folder.isdigit():
            numeric_folders.append(int(folder))
        else:
            non_numeric_folders.append(folder)
    
    if numeric_folders:
        numeric_folders.sort()
        print(f"Numeric folders: {len(numeric_folders)}")
        print(f"Range: {min(numeric_folders)} to {max(numeric_folders)}")
        print()
        
        # Check if starts from 0 or 1
        if min(numeric_folders) == 0:
            print("Status: Already starts from 0 (0-based indexing)")
        elif min(numeric_folders) == 1:
            print("Status: Starts from 1 (1-based indexing)")
            print("→ Recommend: Subtract 1 to convert to 0-based indexing")
        else:
            print(f"Status: Starts from {min(numeric_folders)}")
        
        # Check for gaps
        expected_range = set(range(min(numeric_folders), max(numeric_folders) + 1))
        actual_numbers = set(numeric_folders)
        missing = expected_range - actual_numbers
        
        if missing:
            print(f"\nWarning: Missing numbers in sequence: {sorted(missing)}")
        else:
            print("\n All numbers are consecutive")
        
        # Show samples
        print(f"\nSample folders (first 15):")
        for num in numeric_folders[:15]:
            print(f"  {num} -> {num - 1} (after subtracting 1)")
        if len(numeric_folders) > 15:
            print(f"  ... and {len(numeric_folders) - 15} more")
    
    if non_numeric_folders:
        print(f"\n\nNon-numeric folders: {len(non_numeric_folders)}")
        print("These will be skipped during renaming:")
        for folder in non_numeric_folders[:10]:
            print(f"  - {folder}")
        if len(non_numeric_folders) > 10:
            print(f"  ... and {len(non_numeric_folders) - 10} more")

if __name__ == "__main__":
    # ==========================================
    # Decrement all folder numbers by 1
    # ==========================================
    directory_path = r"F:\archive\organized_by_identity"
    
    print("="*60)
    print("Folder Renaming: Subtract 1 from Each Folder (SAFE METHOD)")
    print("="*60)
    print(f"Directory: {directory_path}")
    print(f"Conversion: 1-based -> 0-based indexing")
    print(f"Method: Two-phase renaming with temporary names")
    print("="*60)
    print()
    
    # Step 0: Analyze current state (recommended)
    print("STEP 0: ANALYZE CURRENT STATE")
    print("="*60)
    analyze_numeric_folders(directory_path)
    
    # Step 1: Preview renaming
    print("\n\nSTEP 1: PREVIEW MODE")
    print("="*60)
    rename_folders_decrement_safe(directory_path, dry_run=True)
    
    # Step 2: Uncomment below to perform actual renaming
    print("\n\nSTEP 2: ACTUAL RENAMING")
    print("="*60)
    rename_folders_decrement_safe(directory_path, dry_run=False)
    
    # Step 3: Verify after renaming
    # print("\n\nSTEP 3: VERIFICATION")
    # verify_after_decrement(directory_path)