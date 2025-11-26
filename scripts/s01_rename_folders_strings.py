import os
import re
from pathlib import Path
from collections import defaultdict

def rename_folders_with_mapping(directory_path, prefix_to_remove=None, dry_run=True):
    """
    Rename folders by creating a mapping from unique names to sequential numbers starting from 0
    
    Args:
        directory_path: Path to the directory containing folders to rename
        prefix_to_remove: Optional prefix to remove before sorting (e.g., ' ReunionTurtles_')
        dry_run: If True, only preview changes without actually renaming
    
    Examples:
        ' ReunionTurtles_Akrouba' -> '0'
        ' ReunionTurtles_Akwaba' -> '1'
        ' ReunionTurtles_Zulu' -> '2'
        (alphabetically sorted after removing prefix)
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
    if prefix_to_remove:
        print(f"Removing prefix: '{prefix_to_remove}'")
    print("="*60)
    
    # Create sorted list of folders for consistent mapping
    # Extract the meaningful part (after prefix) for sorting
    folder_sort_keys = []
    for folder in folders:
        if prefix_to_remove and folder.startswith(prefix_to_remove):
            sort_key = folder[len(prefix_to_remove):]
        else:
            sort_key = folder
        folder_sort_keys.append((folder, sort_key))
    
    # Sort by the sort key (alphabetically)
    folder_sort_keys.sort(key=lambda x: x[1].lower())
    
    # Create mapping from old name to new ID
    folder_mapping = {}
    for idx, (folder_name, sort_key) in enumerate(folder_sort_keys):
        folder_mapping[folder_name] = idx
    
    # Display mapping
    print("\nFolder to ID Mapping (sorted alphabetically):")
    print("-"*60)
    for folder_name, new_id in sorted(folder_mapping.items(), key=lambda x: x[1]):
        print(f"  '{folder_name}' -- '{new_id}'")
    print("-"*60)
    
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
        
        rename_operations.append((old_path, new_path, folder_name, new_name))
    
    # Display rename preview
    print(f"\nTotal: {len(rename_operations)} folders to rename")
    if skipped_folders:
        print(f"Skipped: {len(skipped_folders)} folders (conflicts detected)")
    
    # Perform renaming
    if dry_run:
        print("\n[DRY RUN MODE] No changes made.")
        print("Set dry_run=False to perform actual renaming.")
    else:
        print("\nPerforming renaming...")
        success_count = 0
        failed_count = 0
        
        for old_path, new_path, old_name, new_name in rename_operations:
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


def analyze_folder_patterns(directory_path):
    """
    Analyze folder naming patterns to help determine the best renaming strategy
    
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
    print("Folder Pattern Analysis")
    print("="*60)
    print(f"Total folders: {len(folders)}")
    print()
    
    # Detect common prefixes
    prefix_counts = defaultdict(int)
    for folder in folders:
        parts = folder.split('_')
        if len(parts) > 1:
            prefix = parts[0] + '_'
            prefix_counts[prefix] += 1
    
    if prefix_counts:
        print("Detected prefixes:")
        for prefix, count in sorted(prefix_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  '{prefix}' appears {count} times")
        most_common_prefix = max(prefix_counts.items(), key=lambda x: x[1])[0]
        print(f"\nRecommended prefix to remove: '{most_common_prefix}'")
    else:
        print("No common prefix detected")
    
    # Show sample folders
    print("\nSample folders (first 10):")
    for folder in sorted(folders)[:10]:
        print(f"  {folder}")
    if len(folders) > 10:
        print(f"  ... and {len(folders) - 10} more")


def save_mapping_to_file(directory_path, prefix_to_remove=None, output_file="folder_mapping.txt"):
    """
    Save the folder mapping to a text file for reference
    
    Args:
        directory_path: Path to the directory containing folders
        prefix_to_remove: Optional prefix to remove before sorting
        output_file: Output file name
    """
    items = os.listdir(directory_path)
    folders = [item for item in items if os.path.isdir(os.path.join(directory_path, item))]
    
    # Create sorted mapping
    folder_sort_keys = []
    for folder in folders:
        if prefix_to_remove and folder.startswith(prefix_to_remove):
            sort_key = folder[len(prefix_to_remove):]
        else:
            sort_key = folder
        folder_sort_keys.append((folder, sort_key))
    
    folder_sort_keys.sort(key=lambda x: x[1].lower())
    
    # Write to file
    output_path = os.path.join(directory_path, output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("Original Folder Name -- New ID\n")
        f.write("="*60 + "\n")
        for idx, (folder_name, sort_key) in enumerate(folder_sort_keys):
            f.write(f"{folder_name} -- {idx}\n")

    print(f"\nMapping saved to: {output_path}")


if __name__ == "__main__":
    # ==========================================
    # Example:  ReunionTurtles folders
    # ==========================================
    # directory_path = r"F:\archive\organized_by_identity"
    directory_path = r"F:\archive\data\WildRaptorID\IDs"
    
    # Step 0: Analyze folder patterns (recommended first step)
    print("STEP 0: ANALYZE FOLDER PATTERNS")
    print("="*60)
    # analyze_folder_patterns(directory_path)
    
    # Step 1: Preview with prefix removal
    print("\n\nSTEP 1: PREVIEW MODE")
    rename_folders_with_mapping(
        directory_path, 
        prefix_to_remove="w_",  # Change this to match your prefix
        dry_run=True
    )
    
    # Step 2: Save mapping to file (recommended before actual renaming)
    save_mapping_to_file(directory_path, prefix_to_remove="w_")
    
    # Step 3: Uncomment below to perform actual renaming
    print("\n\nSTEP 3: ACTUAL RENAMING")
    rename_folders_with_mapping(
        directory_path, 
        prefix_to_remove="w_",
        dry_run=False
    )