import os
import re
from pathlib import Path

def rename_folders_extract_and_offset(directory_path, prefix_pattern=None, offset=-1, dry_run=True):
    """
    Rename folders by extracting number from name and applying an offset
    
    Args:
        directory_path: Path to the directory containing folders to rename
        prefix_pattern: Prefix pattern to match (e.g., 'Cow', 'Dog', 'Cat')
                       If None, will try to auto-detect
        offset: Number to add to extracted number (use -1 to convert 1-based to 0-based)
        dry_run: If True, only preview changes without actually renaming
    
    Examples with offset=-1:
        'Cow1' -> '0' (1-1=0)
        'Cow2' -> '1' (2-1=1)
        'Cow10' -> '9' (10-1=9)
        'Cow123' -> '122' (123-1=122)
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
    
    # Auto-detect prefix if not provided
    if prefix_pattern is None:
        # Try to detect common prefix pattern (letters followed by numbers)
        sample_folder = folders[0]
        match = re.match(r'^([A-Za-z]+)\d+$', sample_folder)
        if match:
            prefix_pattern = match.group(1)
            print(f"Auto-detected prefix: '{prefix_pattern}'")
        else:
            print("Could not auto-detect prefix pattern")
            return
    
    print(f"Prefix pattern: '{prefix_pattern}'")
    print(f"Offset: {offset}")
    print("="*60)
    
    # Store rename operations
    rename_operations = []
    skipped_folders = []
    
    for folder_name in sorted(folders):
        old_path = os.path.join(directory_path, folder_name)
        
        # Extract number from folder name
        # Match pattern like 'Cow1', 'Cow2', 'Cow123'
        pattern = rf'^{re.escape(prefix_pattern)}(\d+)$'
        match = re.match(pattern, folder_name)
        
        if not match:
            print(f"Skipping '{folder_name}' (doesn't match pattern '{prefix_pattern}###')")
            skipped_folders.append(folder_name)
            continue
        
        original_number = int(match.group(1))
        
        # Apply offset
        new_number = original_number + offset
        
        # Check if new number is negative
        if new_number < 0:
            print(f"Warning: '{folder_name}' would become {new_number} (negative), skipping")
            skipped_folders.append(folder_name)
            continue
        
        new_name = str(new_number)
        new_path = os.path.join(directory_path, new_name)
        
        # Check if target name already exists
        if os.path.exists(new_path):
            print(f"Warning: Target '{new_name}' already exists, skipping '{folder_name}'")
            skipped_folders.append(folder_name)
            continue
        
        rename_operations.append((old_path, new_path, folder_name, new_name, original_number, new_number))
    
    # Display preview
    if rename_operations:
        print("\nRename Preview:")
        print("-"*60)
        for old_path, new_path, old_name, new_name, orig_num, new_num in rename_operations:
            print(f"  '{old_name}' (ID={orig_num}) -> '{new_name}' (ID={new_num})")
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
    else:
        print("\nPerforming renaming...")
        success_count = 0
        failed_count = 0
        
        for old_path, new_path, old_name, new_name, orig_num, new_num in rename_operations:
            try:
                os.rename(old_path, new_path)
                print(f"Renamed: '{old_name}' -- '{new_name}'")
                success_count += 1
            except Exception as e:
                print(f"Failed to rename '{old_name}': {e}")
                failed_count += 1
        
        print("\n" + "="*60)
        print("Renaming Complete!")
        print("="*60)
        print(f"Successfully renamed: {success_count} folders")
        print(f"Failed: {failed_count} folders")


def analyze_prefix_patterns(directory_path):
    """
    Analyze folder naming patterns to detect prefix
    
    Args:
        directory_path: Path to the directory to analyze
    """
    if not os.path.exists(directory_path):
        print(f"Error: Directory not found: {directory_path}")
        return None
    
    items = os.listdir(directory_path)
    folders = [item for item in items if os.path.isdir(os.path.join(directory_path, item))]
    
    if not folders:
        print("No folders found.")
        return None
    
    print("="*60)
    print("Folder Pattern Analysis")
    print("="*60)
    print(f"Total folders: {len(folders)}")
    print()
    
    # Try to detect pattern (letters followed by numbers)
    patterns = {}
    for folder in folders:
        match = re.match(r'^([A-Za-z]+)(\d+)$', folder)
        if match:
            prefix = match.group(1)
            number = int(match.group(2))
            if prefix not in patterns:
                patterns[prefix] = []
            patterns[prefix].append(number)
    
    if patterns:
        print("Detected patterns:")
        for prefix, numbers in patterns.items():
            print(f"  '{prefix}': {len(numbers)} folders")
            print(f"    Number range: {min(numbers)} to {max(numbers)}")
            print(f"    Example: {prefix}{numbers[0]}")
        
        # Recommend most common prefix
        most_common = max(patterns.items(), key=lambda x: len(x[1]))
        print(f"\nRecommended prefix: '{most_common[0]}'")
        return most_common[0]
    else:
        print("No standard pattern detected (expecting format like 'Cow1', 'Dog2', etc.)")
        print("\nSample folders:")
        for folder in sorted(folders)[:10]:
            print(f"  {folder}")
        return None


def verify_sequential_ids(directory_path):
    """
    Verify that folder IDs are sequential after renaming
    
    Args:
        directory_path: Path to the directory to verify
    """
    items = os.listdir(directory_path)
    folders = [item for item in items if os.path.isdir(os.path.join(directory_path, item))]
    
    # Extract numbers from folder names
    folder_numbers = []
    for folder in folders:
        if folder.isdigit():
            folder_numbers.append(int(folder))
    
    if not folder_numbers:
        print("No numeric folders found.")
        return
    
    folder_numbers.sort()
    
    print("\n" + "="*60)
    print("Verification Report")
    print("="*60)
    print(f"Total folders: {len(folder_numbers)}")
    print(f"ID range: {min(folder_numbers)} to {max(folder_numbers)}")
    print(f"Expected range (0-based): 0 to {len(folder_numbers)-1}")
    
    # Check for missing IDs
    expected_ids = set(range(min(folder_numbers), max(folder_numbers) + 1))
    actual_ids = set(folder_numbers)
    missing_ids = expected_ids - actual_ids
    
    if missing_ids:
        print(f"\nWarning: Missing IDs: {sorted(missing_ids)}")
    else:
        print("\nAll IDs are consecutive")
    
    # Check if starts from 0
    if min(folder_numbers) == 0:
        print("IDs start from 0")
    else:
        print(f"Warning: IDs start from {min(folder_numbers)}, not 0")


if __name__ == "__main__":
    # ==========================================
    # Cow1, Cow2, ... renaming
    # ==========================================
    directory_path = r"F:\archive\data\FriesianCattle2015\IDs"
    
    print("="*60)
    print("Folder Renaming: Prefix+Number -- 0-based ID")
    print("="*60)
    print(f"Directory: {directory_path}")
    print()
    
    # Step 0: Analyze patterns (recommended first step)
    print("STEP 0: ANALYZE FOLDER PATTERNS")
    print("="*60)
    detected_prefix = analyze_prefix_patterns(directory_path)
    
    # Step 1: Preview with detected or manual prefix
    print("\n\nSTEP 1: PREVIEW MODE")
    print("="*60)
    
    # Option A: Use auto-detected prefix
    rename_folders_extract_and_offset(
        directory_path,
        prefix_pattern=detected_prefix,  # Use detected prefix (e.g., 'Cow')
        # prefix_pattern="Cow",  # Or specify manually
        offset=-1,  # Convert 1-based to 0-based
        dry_run=True
    )
    
    # Step 2: Uncomment below to perform actual renaming
    print("\n\nSTEP 2: ACTUAL RENAMING")
    print("="*60)
    rename_folders_extract_and_offset(
        directory_path,
        prefix_pattern="Cow",  # Change to your prefix
        offset=-1,
        dry_run=False
    )
    
    # Step 3: Verify after renaming (uncomment after actual renaming)
    # print("\n\nSTEP 3: VERIFICATION")
    # verify_sequential_ids(directory_path)