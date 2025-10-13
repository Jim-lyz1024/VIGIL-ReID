import os
import shutil
from pathlib import Path

def rename_folders_remove_prefix(directory_path, prefix_to_remove=None, dry_run=True):
    """
    Rename folders by removing prefix before underscore, keeping only the number after underscore
    
    Args:
        directory_path: Path to the directory containing folders to rename
        prefix_to_remove: Specific prefix to remove (e.g., 'AerialCattle2017'). 
                         If None, removes everything before the last underscore
        dry_run: If True, only preview changes without actually renaming. 
                If False, perform actual renaming.
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
    print("="*60)
    
    # Store rename operations
    rename_operations = []
    
    for folder_name in sorted(folders):
        old_path = os.path.join(directory_path, folder_name)
        
        # Determine new name
        if prefix_to_remove:
            # Remove specific prefix
            if folder_name.startswith(prefix_to_remove + "_"):
                new_name = folder_name[len(prefix_to_remove) + 1:]
            else:
                print(f"Skipping '{folder_name}' (doesn't match prefix '{prefix_to_remove}_')")
                continue
        else:
            # Remove everything before the last underscore
            if "_" in folder_name:
                new_name = folder_name.split("_")[-1]
            else:
                print(f"Skipping '{folder_name}' (no underscore found)")
                continue
        
        new_path = os.path.join(directory_path, new_name)
        
        # Check if target name already exists
        if os.path.exists(new_path):
            print(f"Warning: Target '{new_name}' already exists, skipping '{folder_name}'")
            continue
        
        rename_operations.append((old_path, new_path, folder_name, new_name))
    
    # Display preview
    if rename_operations:
        print("\nRename Preview:")
        print("-"*60)
        for old_path, new_path, old_name, new_name in rename_operations:
            print(f"  '{old_name}' -> '{new_name}'")
        print("-"*60)
        print(f"Total: {len(rename_operations)} folders to rename")
    else:
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
        
        for old_path, new_path, old_name, new_name in rename_operations:
            try:
                os.rename(old_path, new_path)
                print(f" Renamed: '{old_name}' -- '{new_name}'")
                success_count += 1
            except Exception as e:
                print(f" Failed to rename '{old_name}': {e}")
                failed_count += 1
        
        print("\n" + "="*60)
        print("Renaming Complete!")
        print("="*60)
        print(f"Successfully renamed: {success_count} folders")
        print(f"Failed: {failed_count} folders")


def batch_rename_multiple_directories(base_paths_with_prefixes, dry_run=True):
    """
    Batch rename folders in multiple directories
    
    Args:
        base_paths_with_prefixes: List of tuples (directory_path, prefix_to_remove)
        dry_run: If True, only preview changes without actually renaming
    
    Example:
        base_paths_with_prefixes = [
            ("E:/path1/IDs", "AerialCattle2017"),
            ("E:/path2/IDs", "AAUZebraFish"),
        ]
    """
    for directory_path, prefix in base_paths_with_prefixes:
        print("\n" + "="*60)
        print(f"Processing: {directory_path}")
        print(f"Removing prefix: {prefix}")
        print("="*60)
        rename_folders_remove_prefix(directory_path, prefix, dry_run)


if __name__ == "__main__":
    # ==========================================
    # Single Directory Mode
    # ==========================================
    directory_path = r"F:\archive\data\Chicks4FreeID\IDs"
    prefix_to_remove = "Chicks4FreeID"  # Remove this prefix before underscore

    # Step 1: Preview changes (dry_run=True)
    print("STEP 1: PREVIEW MODE")
    print("="*60)
    rename_folders_remove_prefix(directory_path, prefix_to_remove, dry_run=True)
    rename_folders_remove_prefix(directory_path, prefix_to_remove, dry_run=False)
    
    # Step 2: Uncomment below to perform actual renaming
    # print("\n\nSTEP 2: ACTUAL RENAMING")
    # print("="*60)
    # rename_folders_remove_prefix(directory_path, prefix_to_remove, dry_run=False)
    
    # ==========================================
    # Batch Mode: Process Multiple Directories
    # ==========================================
    # Uncomment below to process multiple directories at once
    """
    base_paths_with_prefixes = [
        (r"E:\LYZ\AucklandCourse\2024Thesis\Thesis\VIGIL-ReID\data\AerialCattle2017\IDs", "AerialCattle2017"),
        (r"E:\LYZ\AucklandCourse\2024Thesis\Thesis\VIGIL-ReID\data\AAUZebraFish\IDs", "AAUZebraFish"),
        # Add more paths as needed
    ]
    
    # Preview
    print("BATCH PREVIEW MODE")
    batch_rename_multiple_directories(base_paths_with_prefixes, dry_run=True)
    
    # Uncomment to perform actual renaming
    # print("\n\nBATCH ACTUAL RENAMING")
    # batch_rename_multiple_directories(base_paths_with_prefixes, dry_run=False)
    """