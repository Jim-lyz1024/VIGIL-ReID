import os
import re
from pathlib import Path

def rename_folders_sorted_sequential(directory_path, sort_by='number', dry_run=True):
    """
    Rename folders to sequential numbers (0, 1, 2, ...) based on sorting
    
    Args:
        directory_path: Path to the directory containing folders to rename
        sort_by: Sorting method
                 - 'number': Sort by extracted number (e.g., cluster2 < cluster4 < cluster10)
                 - 'alphabet': Sort alphabetically (e.g., cluster10 < cluster2 < cluster4)
        dry_run: If True, only preview changes without actually renaming
    
    Examples with sort_by='number':
        'Giraffes_cluster2' -> '0' (1st in sorted order)
        'Giraffes_cluster4' -> '1' (2nd in sorted order)
        'Giraffes_cluster10' -> '2' (3rd in sorted order)
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
    print(f"Sort method: {sort_by}")
    print("="*60)
    
    # Create list of (folder_name, sort_key)
    folder_sort_data = []
    for folder_name in folders:
        if sort_by == 'number':
            # Extract all numbers from folder name
            numbers = re.findall(r'\d+', folder_name)
            if numbers:
                # Use the last number as sort key (convert to int for proper numeric sorting)
                sort_key = int(numbers[-1])
            else:
                # If no number found, use alphabetical sorting as fallback
                sort_key = folder_name
        else:  # alphabet
            sort_key = folder_name.lower()
        
        folder_sort_data.append((folder_name, sort_key))
    
    # Sort by the sort key
    if sort_by == 'number':
        # For numeric sorting, handle mixed types (int and str)
        folder_sort_data.sort(key=lambda x: (isinstance(x[1], str), x[1]))
    else:
        folder_sort_data.sort(key=lambda x: x[1])
    
    # Display sorted order
    print("\nSorted Order:")
    print("-"*60)
    for idx, (folder_name, sort_key) in enumerate(folder_sort_data):
        print(f"  {idx}: '{folder_name}' (sort_key={sort_key})")
    print("-"*60)
    
    # Create mapping from old name to new ID
    folder_mapping = {}
    for idx, (folder_name, _) in enumerate(folder_sort_data):
        folder_mapping[folder_name] = idx
    
    # Store rename operations
    rename_operations = []
    skipped_folders = []
    
    for folder_name in folders:
        old_path = os.path.join(directory_path, folder_name)
        new_name = str(folder_mapping[folder_name])
        new_path = os.path.join(directory_path, new_name)
        
        # Check if target name already exists
        if os.path.exists(new_path):
            print(f"Warning: Target '{new_name}' already exists, skipping '{folder_name}'")
            skipped_folders.append(folder_name)
            continue
        
        rename_operations.append((old_path, new_path, folder_name, new_name, folder_mapping[folder_name]))
    
    # Display rename preview
    print(f"\nRename Preview:")
    print("-"*60)
    for old_path, new_path, old_name, new_name, new_id in sorted(rename_operations, key=lambda x: x[4]):
        print(f"  '{old_name}' -> '{new_name}'")
    print("-"*60)
    print(f"Total: {len(rename_operations)} folders to rename")
    
    if skipped_folders:
        print(f"\nSkipped: {len(skipped_folders)} folders (conflicts detected)")
        for folder in skipped_folders:
            print(f"  - {folder}")
    
    if not rename_operations:
        print("No folders to rename.")
        return
    
    # Perform renaming
    if dry_run:
        print("\n[DRY RUN MODE] No changes made.")
        print("Set dry_run=False to perform actual renaming.")
    else:
        print("\nPerforming renaming...")
        success_count = 0
        failed_count = 0
        
        for old_path, new_path, old_name, new_name, _ in rename_operations:
            try:
                os.rename(old_path, new_path)
                print(f"Renamed: '{old_name}' -> '{new_name}'")
                success_count += 1
            except Exception as e:
                print(f"Failed to rename '{old_name}': {e}")
                failed_count += 1
        
        print("\n" + "="*60)
        print("Renaming Complete!")
        print("="*60)
        print(f"Successfully renamed: {success_count} folders")
        print(f"Failed: {failed_count} folders")


def analyze_folder_structure(directory_path):
    """
    Analyze folder naming structure to understand the pattern
    
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
    print("Folder Structure Analysis")
    print("="*60)
    print(f"Total folders: {len(folders)}")
    print()
    
    # Extract numbers from folder names
    folders_with_numbers = []
    for folder in folders:
        numbers = re.findall(r'\d+', folder)
        if numbers:
            folders_with_numbers.append((folder, [int(n) for n in numbers]))
    
    if folders_with_numbers:
        print("Folders with numbers:")
        print("-"*60)
        for folder, numbers in sorted(folders_with_numbers, key=lambda x: x[1][-1])[:15]:
            print(f"  {folder} -> numbers: {numbers}")
        if len(folders_with_numbers) > 15:
            print(f"  ... and {len(folders_with_numbers) - 15} more")
        
        # Show number range
        all_last_numbers = [nums[-1] for _, nums in folders_with_numbers]
        print(f"\nNumber range (last number in name): {min(all_last_numbers)} to {max(all_last_numbers)}")
        print(f"Total unique numbers: {len(set(all_last_numbers))}")
    
    # Show alphabetical order sample
    print("\n\nAlphabetical order (first 10):")
    print("-"*60)
    for idx, folder in enumerate(sorted(folders)[:10]):
        print(f"  {idx}: {folder}")
    
    # Show numeric order sample (if applicable)
    if folders_with_numbers:
        print("\n\nNumeric order by last number (first 10):")
        print("-"*60)
        sorted_by_number = sorted(folders_with_numbers, key=lambda x: x[1][-1])
        for idx, (folder, numbers) in enumerate(sorted_by_number[:10]):
            print(f"  {idx}: {folder} (number={numbers[-1]})")


def save_mapping_file(directory_path, sort_by='number', output_file="folder_mapping.txt"):
    """
    Save the folder mapping to a text file for reference
    
    Args:
        directory_path: Path to the directory
        sort_by: Sorting method ('number' or 'alphabet')
        output_file: Output file name
    """
    items = os.listdir(directory_path)
    folders = [item for item in items if os.path.isdir(os.path.join(directory_path, item))]
    
    # Create sorted list
    folder_sort_data = []
    for folder_name in folders:
        if sort_by == 'number':
            numbers = re.findall(r'\d+', folder_name)
            sort_key = int(numbers[-1]) if numbers else folder_name
        else:
            sort_key = folder_name.lower()
        folder_sort_data.append((folder_name, sort_key))
    
    if sort_by == 'number':
        folder_sort_data.sort(key=lambda x: (isinstance(x[1], str), x[1]))
    else:
        folder_sort_data.sort(key=lambda x: x[1])
    
    # Write to file
    output_path = os.path.join(directory_path, output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"Folder Mapping (sorted by: {sort_by})\n")
        f.write("="*60 + "\n")
        f.write("Original Folder Name -> New ID\n")
        f.write("-"*60 + "\n")
        for idx, (folder_name, sort_key) in enumerate(folder_sort_data):
            f.write(f"{folder_name} -> {idx} (sort_key={sort_key})\n")
    
    print(f"\nMapping saved to: {output_path}")


if __name__ == "__main__":
    # ==========================================
    # Giraffes_cluster2, Giraffes_cluster4, ... renaming
    # ==========================================
    directory_path = r"F:\archive\organized_by_identity"
    
    print("="*60)
    print("Folder Renaming: Sorted Sequential (0, 1, 2, ...)")
    print("="*60)
    print(f"Directory: {directory_path}\n")
    
    # Step 0: Analyze folder structure (recommended)
    print("STEP 0: ANALYZE FOLDER STRUCTURE")
    print("="*60)
    analyze_folder_structure(directory_path)
    
    # Step 1: Preview with numeric sorting (default)
    # print("\n\nSTEP 1: PREVIEW MODE (Numeric Sorting)")
    # print("="*60)
    # rename_folders_sorted_sequential(
    #     directory_path,
    #     sort_by='number',  # Sort by extracted number
    #     dry_run=True
    # )
    
    # Alternative: Preview with alphabetical sorting
    print("\n\nSTEP 1 (Alternative): PREVIEW MODE (Alphabetical Sorting)")
    print("="*60)
    rename_folders_sorted_sequential(
        directory_path,
        sort_by='alphabet',
        dry_run=True
    )
    
    # # Step 2: Save mapping to file (recommended)
    # save_mapping_file(directory_path, sort_by='number')
    
    # # Step 3: Uncomment below to perform actual renaming
    # print("\n\nSTEP 3: ACTUAL RENAMING")
    # print("="*60)
    # rename_folders_sorted_sequential(
    #     directory_path,
    #     sort_by='number',  # or 'alphabet'
    #     dry_run=False
    # )