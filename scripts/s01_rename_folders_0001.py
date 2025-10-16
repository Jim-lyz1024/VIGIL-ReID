import os
import re
from pathlib import Path

def rename_folders_with_offset(directory_path, offset=-1, dry_run=True):
    """
    Rename folders by extracting number and applying an offset
    
    Args:
        directory_path: Path to the directory containing folders to rename
        offset: Number to add to the extracted number (use -1 to convert 1-based to 0-based)
        dry_run: If True, only preview changes without actually renaming
    
    Examples with offset=-1:
        '0001' -> '0' (1-1=0)
        '0002' -> '1' (2-1=1)
        '0010' -> '9' (10-1=9)
        '0123' -> '122' (123-1=122)
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
    print(f"Offset: {offset}")
    print("="*60)
    
    # Store rename operations
    rename_operations = []
    skipped_folders = []
    
    for folder_name in sorted(folders):
        old_path = os.path.join(directory_path, folder_name)
        
        # Extract number from folder name
        # Try to match pure number folders first (like '0001', '0002')
        if folder_name.isdigit():
            original_number = int(folder_name)
        else:
            # If not pure digits, extract the last number sequence
            numbers = re.findall(r'\d+', folder_name)
            if not numbers:
                print(f"Skipping '{folder_name}' (no numbers found)")
                skipped_folders.append(folder_name)
                continue
            original_number = int(numbers[-1])
        
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


def verify_folders_after_rename(directory_path):
    """
    Verify folder names after renaming to check for issues
    
    Args:
        directory_path: Path to the directory to verify
    """
    items = os.listdir(directory_path)
    folders = [item for item in items if os.path.isdir(os.path.join(directory_path, item))]
    
    if not folders:
        print("No folders found.")
        return
    
    print("\n" + "="*60)
    print("Verification Report")
    print("="*60)
    
    # Extract numbers from folder names
    folder_numbers = []
    for folder in folders:
        if folder.isdigit():
            folder_numbers.append(int(folder))
        else:
            numbers = re.findall(r'\d+', folder)
            if numbers:
                folder_numbers.append(int(numbers[-1]))
    
    if folder_numbers:
        folder_numbers.sort()
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
        
        # Check for duplicate IDs
        if len(folder_numbers) != len(set(folder_numbers)):
            print("Warning: Duplicate IDs found!")
        else:
            print("No duplicate IDs")


if __name__ == "__main__":
    # ==========================================
    # CatIndividualImages Renaming
    # ==========================================
    # directory_path = r"E:\LYZ\AucklandCourse\2024Thesis\Thesis\VIGIL-ReID\data\CatIndividualImages\IDs"
    directory_path = r"F:\archive\organized_by_identity"
    
    print("="*60)
    print("GiraffeZebraID Folder Renaming")
    print("="*60)
    print(f"Directory: {directory_path}")
    print(f"Conversion: 1-based ID -> 0-based ID (subtract 1)")
    print(f"Examples: 0001->0, 0002->1, 0010->9")
    print("="*60)
    print()
    
    # Step 1: Preview changes (dry_run=True)
    print("STEP 1: PREVIEW MODE")
    print("="*60)
    rename_folders_with_offset(directory_path, offset=-1, dry_run=True)
    # rename_folders_with_offset(directory_path, offset=-1, dry_run=False)
    # rename_folders_with_offset(directory_path, offset=-1, dry_run=False)
    
    # Step 2: Uncomment below to perform actual renaming
    # print("\n\nSTEP 2: ACTUAL RENAMING")
    # print("="*60)
    # rename_folders_with_offset(directory_path, offset=-1, dry_run=False)
    
    # Step 3: Verify after renaming (uncomment after actual renaming)
    # print("\n\nSTEP 3: VERIFICATION")
    # verify_folders_after_rename(directory_path)