import os
import shutil
from pathlib import Path

def rename_turtle_images(base_dir):
    """
    Rename turtle images
    
    Args:
        base_dir: Base directory containing ID folders
    
    Format: id_-1_index_original.JPG
    Example: 0_-1_0_01_2017_left_DSC03532_0.JPG
    """
    base_path = Path(base_dir)
    
    if not base_path.exists():
        print(f"Error: Directory does not exist {base_dir}")
        return
    
    # Get all numeric subfolders and sort them
    id_folders = sorted([f for f in base_path.iterdir() 
                        if f.is_dir() and f.name.isdigit()], 
                       key=lambda x: int(x.name))
    
    print(f"Found {len(id_folders)} ID folders")
    print("-" * 80)
    
    total_renamed = 0
    
    # Iterate through each ID folder
    for folder in id_folders:
        turtle_id = int(folder.name)
        print(f"\nProcessing ID: {turtle_id} (Folder: {folder.name})")
        
        # Get all image files in the folder and sort them
        image_files = sorted([f for f in folder.iterdir() 
                            if f.suffix.upper() in ['.JPG', '.JPEG', '.PNG']])
        
        if not image_files:
            print(f"  Warning: No images found in folder {folder.name}")
            continue
        
        print(f"  Found {len(image_files)} images")
        
        # Rename each image
        for index, img_file in enumerate(image_files):
            original_name = img_file.name
            original_name_without_ext = img_file.stem
            ext = img_file.suffix
            
            # New filename format: id_-1_index_original
            new_name = f"{turtle_id}_-1_{index}_{original_name}"
            new_path = img_file.parent / new_name
            
            # Rename file
            try:
                img_file.rename(new_path)
                total_renamed += 1
                
                # Print only first 3 and last one to avoid excessive output
                if index < 3 or index == len(image_files) - 1:
                    print(f"    [{index}] {original_name}")
                    print(f"      -> {new_name}")
                elif index == 3:
                    print(f"    ... (total {len(image_files)} images)")
                    
            except Exception as e:
                print(f"  Error: Failed to rename {original_name}: {e}")
    
    print("\n" + "=" * 80)
    print(f"Renaming completed! Total processed: {total_renamed} images")
    print("=" * 80)


def verify_renaming(base_dir):
    """
    Verify renaming results
    """
    base_path = Path(base_dir)
    
    print("\nVerifying renaming results:")
    print("-" * 80)
    
    id_folders = sorted([f for f in base_path.iterdir() 
                        if f.is_dir() and f.name.isdigit()], 
                       key=lambda x: int(x.name))
    
    for folder in id_folders:
        turtle_id = int(folder.name)
        image_files = sorted([f for f in folder.iterdir() 
                            if f.suffix.upper() in ['.JPG', '.JPEG', '.PNG']])
        
        print(f"\nID {turtle_id}: {len(image_files)} images")
        
        # Check naming format of first 3 images
        for i, img in enumerate(image_files[:3]):
            expected_prefix = f"{turtle_id}_-1_{i}_"
            if img.name.startswith(expected_prefix):
                print(f"{img.name}")
            else:
                print(f"{img.name} (expected prefix: {expected_prefix})")
        
        if len(image_files) > 3:
            print(f"  ... and {len(image_files) - 3} more images")


if __name__ == "__main__":
    # Set base directory
    ############# Change here to specify new dataset #############
    # base_directory = r"E:\LYZ\AucklandCourse\2024Thesis\Thesis\VIGIL-ReID\data\BirdIndividualID\IDs"
    base_directory = r"F:\archive\data\WildRaptorID\IDs"
    #############
    
    print("=" * 80)
    print("Turtle Image Renaming Script")
    print("=" * 80)
    print(f"Target directory: {base_directory}")
    print(f"Naming format: id_-1_index_original.JPG")
    print("=" * 80)
    
    rename_turtle_images(base_directory)
    verify_renaming(base_directory)