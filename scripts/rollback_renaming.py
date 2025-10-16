import os
from pathlib import Path

def rollback_renaming(base_dir):
    """
    Rollback renaming: remove id_-1_index_ prefix
    
    Example: 0_-1_0_01_2017_left_DSC03532_0.JPG -> 01_2017_left_DSC03532_0.JPG
    """
    base_path = Path(base_dir)
    
    if not base_path.exists():
        print(f"Error: Directory does not exist {base_dir}")
        return
    
    id_folders = sorted([f for f in base_path.iterdir() 
                        if f.is_dir() and f.name.isdigit()], 
                       key=lambda x: int(x.name))
    
    print(f"Found {len(id_folders)} ID folders")
    print("-" * 80)
    
    total_restored = 0
    
    for folder in id_folders:
        turtle_id = int(folder.name)
        print(f"\nProcessing ID: {turtle_id}")
        
        image_files = sorted([f for f in folder.iterdir() 
                            if f.suffix.upper() in ['.JPG', '.JPEG', '.PNG']])
        
        for img_file in image_files:
            original_name = img_file.name
            
            # Check if file follows the renamed pattern
            prefix = f"{turtle_id}_-1_"
            if original_name.startswith(prefix):
                # Remove prefix (id_-1_index_)
                parts = original_name.split('_', 3)
                if len(parts) >= 4:
                    restored_name = parts[3]  # Get original filename
                    new_path = img_file.parent / restored_name
                    
                    try:
                        img_file.rename(new_path)
                        total_restored += 1
                        print(f"  Restored: {original_name} -> {restored_name}")
                    except Exception as e:
                        print(f"  Error: Failed to restore {original_name}: {e}")
            else:
                print(f"  Skipped: {original_name} (doesn't match pattern)")
    
    print("\n" + "=" * 80)
    print(f"Rollback completed! Total restored: {total_restored} images")
    print("=" * 80)


if __name__ == "__main__":
    # base_directory = r"E:\LYZ\AucklandCourse\2024Thesis\Thesis\VIGIL-ReID\data\AmvrakikosTurtles\IDs"
    base_directory = r"F:\archive\data\Giraffes\IDs"
    
    print("=" * 80)
    print("Turtle Image Rollback Script")
    print("=" * 80)
    print(f"Target directory: {base_directory}")
    print("=" * 80)
    
    rollback_renaming(base_directory)