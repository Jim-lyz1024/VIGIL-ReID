import os
import shutil
from pathlib import Path
from collections import defaultdict

def collect_raptor_images_by_id(source_base_path, output_path, dry_run=True):
    """
    Collect raptor images from train and Test directories and organize by ID
    
    Args:
        source_base_path: Base path containing train and Test subdirectories
        output_path: Output path for organized images (IDs directory)
        dry_run: If True, only preview changes without actually copying files
    
    Structure:
        Source: source_base_path/train/[id]/images
                source_base_path/Test/[id]/images
        Target: output_path/[id]/images
    
    Example:
        source_base_path/train/ID001/*.jpg -> output_path/ID001/train_*.jpg
        source_base_path/Test/ID001/*.jpg -> output_path/ID001/Test_*.jpg
    """
    # Check if source base path exists
    if not os.path.exists(source_base_path):
        print(f"Error: Source path not found: {source_base_path}")
        return
    
    print("="*60)
    print("WildRaptorID Image Collection by ID")
    print("="*60)
    print(f"Source: {source_base_path}")
    print(f"Target: {output_path}")
    print("="*60)
    print()
    
    # Define subdirectories to scan
    subdirs = ['train', 'Test']
    
    # Collect information about all images
    id_image_mapping = defaultdict(lambda: defaultdict(list))
    total_images = 0
    missing_subdirs = []
    
    # Scan each subdirectory (train and Test)
    for subdir in subdirs:
        subdir_path = os.path.join(source_base_path, subdir)
        
        if not os.path.exists(subdir_path):
            print(f"Warning: '{subdir}' directory not found: {subdir_path}")
            missing_subdirs.append(subdir)
            continue
        
        print(f"Scanning '{subdir}' directory...")
        
        # Get all ID folders in this subdirectory
        try:
            id_folders = [item for item in os.listdir(subdir_path) 
                         if os.path.isdir(os.path.join(subdir_path, item))]
        except PermissionError:
            print(f"   Permission denied: {subdir_path}")
            missing_subdirs.append(subdir)
            continue
        
        if not id_folders:
            print(f"  No ID folders found in '{subdir}'")
            continue
        
        for id_folder in sorted(id_folders):
            raptor_id = id_folder  # Use folder name as ID
            
            id_folder_path = os.path.join(subdir_path, id_folder)
            
            # Get all image files in this folder
            try:
                all_files = os.listdir(id_folder_path)
            except PermissionError:
                print(f"   Permission denied: {id_folder_path}")
                continue
            
            # Common image extensions
            image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff')
            image_files = [f for f in all_files 
                          if f.lower().endswith(image_extensions)]
            
            for image_file in image_files:
                source_file = os.path.join(id_folder_path, image_file)
                id_image_mapping[raptor_id][subdir].append(source_file)
                total_images += 1
        
        print(f"  Found {len(id_folders)} ID folders in '{subdir}'")
    
    print()
    
    # Display statistics
    print("Collection Statistics:")
    print("-"*60)
    print(f"Total IDs found: {len(id_image_mapping)}")
    print(f"Total images to copy: {total_images}")
    
    if missing_subdirs:
        print(f"\nWarning: Could not access: {', '.join(missing_subdirs)}")
    
    # Show image distribution by ID
    print("\nImage Distribution by ID:")
    print("-"*60)
    print(f"{'ID':<20s} {'Train':<12s} {'Test':<12s} {'Total':<8s}")
    print("-"*60)
    
    # Sort IDs
    for raptor_id in sorted(id_image_mapping.keys()):
        train_count = len(id_image_mapping[raptor_id].get('train', []))
        test_count = len(id_image_mapping[raptor_id].get('Test', []))
        total = train_count + test_count
        
        print(f"{raptor_id:<20s} {train_count:<12d} {test_count:<12d} {total:<8d}")
    
    print("-"*60)
    
    # Calculate totals
    total_train = sum(len(id_image_mapping[rid].get('train', [])) 
                     for rid in id_image_mapping.keys())
    total_test = sum(len(id_image_mapping[rid].get('Test', [])) 
                    for rid in id_image_mapping.keys())
    
    print(f"{'Total:':<20s} {total_train:<12d} {total_test:<12d} {total_images:<8d}")
    print("-"*60)
    
    # Perform copying
    if dry_run:
        print("\n[DRY RUN MODE] No files will be copied.")
        print("Set dry_run=False to perform actual copying.")
        
        # Show sample file paths
        print("\nSample file paths (first 3 IDs):")
        for idx, raptor_id in enumerate(sorted(id_image_mapping.keys())):
            if idx >= 3:
                break
            
            print(f"\nID: {raptor_id}")
            for split, files in id_image_mapping[raptor_id].items():
                print(f"  From '{split}': {len(files)} images")
                if files:
                    print(f"    Example: {os.path.basename(files[0])}")
                    target_file = os.path.join(output_path, raptor_id, 
                                              f"{split}_{os.path.basename(files[0])}")
                    print(f"    -> {target_file}")
        
        if len(id_image_mapping) > 3:
            print(f"\n... and {len(id_image_mapping) - 3} more IDs")
    else:
        print("\nCopying files...")
        
        # Create output directory
        os.makedirs(output_path, exist_ok=True)
        
        copied_count = 0
        failed_count = 0
        failed_files = []
        
        for raptor_id in sorted(id_image_mapping.keys()):
            # Create ID folder
            id_output_path = os.path.join(output_path, raptor_id)
            os.makedirs(id_output_path, exist_ok=True)
            
            # Copy images from both train and Test
            for split, source_files in id_image_mapping[raptor_id].items():
                for source_file in source_files:
                    filename = os.path.basename(source_file)
                    # Add split prefix to filename to distinguish train/Test
                    # e.g., train_image.jpg, Test_image.jpg
                    new_filename = f"{split}_{filename}"
                    target_file = os.path.join(id_output_path, new_filename)
                    
                    try:
                        shutil.copy2(source_file, target_file)
                        copied_count += 1
                        
                        # Show progress every 100 files
                        if copied_count % 100 == 0:
                            print(f"  Copied {copied_count} images...")
                    except Exception as e:
                        print(f"  ✗ Failed to copy {source_file}: {e}")
                        failed_count += 1
                        failed_files.append(source_file)
        
        print("\n" + "="*60)
        print("Copying Complete!")
        print("="*60)
        print(f"Successfully copied: {copied_count} images")
        print(f"Failed: {failed_count} images")
        print(f"Total ID folders created: {len(id_image_mapping)}")
        
        if failed_files:
            print("\nFailed files (first 10):")
            for f in failed_files[:10]:
                print(f"  - {f}")
            if len(failed_files) > 10:
                print(f"  ... and {len(failed_files) - 10} more")


def analyze_raptor_structure(source_base_path):
    """
    Analyze the WildRaptorID directory structure
    
    Args:
        source_base_path: Base path containing train and Test subdirectories
    """
    if not os.path.exists(source_base_path):
        print(f"Error: Source path not found: {source_base_path}")
        return
    
    print("="*60)
    print("WildRaptorID Structure Analysis")
    print("="*60)
    print(f"Source: {source_base_path}")
    print()
    
    # Check for train and Test directories
    subdirs = ['train', 'Test']
    
    all_ids = set()
    
    for subdir in subdirs:
        subdir_path = os.path.join(source_base_path, subdir)
        
        if not os.path.exists(subdir_path):
            print(f"{subdir}:")
            print(f"   Directory not found")
            continue
        
        try:
            id_folders = [item for item in os.listdir(subdir_path) 
                         if os.path.isdir(os.path.join(subdir_path, item))]
            
            print(f"{subdir}:")
            print(f"  ID folders: {len(id_folders)}")
            
            if id_folders:
                # Show first 10 IDs
                print(f"  IDs: {', '.join(sorted(id_folders)[:10])}", end='')
                if len(id_folders) > 10:
                    print(f" ... and {len(id_folders) - 10} more")
                else:
                    print()
                
                all_ids.update(id_folders)
                
                # Count images in each ID folder
                total_images = 0
                for id_folder in id_folders:
                    id_path = os.path.join(subdir_path, id_folder)
                    try:
                        files = os.listdir(id_path)
                        image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff')
                        images = [f for f in files if f.lower().endswith(image_extensions)]
                        total_images += len(images)
                    except:
                        pass
                
                print(f"  Total images: {total_images}")
        except PermissionError:
            print(f"{subdir}:")
            print(f"   Permission denied")
        
        print()
    
    print("="*60)
    print(f"Total unique IDs across train and Test: {len(all_ids)}")
    if all_ids:
        sorted_ids = sorted(all_ids)
        print(f"IDs: {', '.join(sorted_ids[:15])}", end='')
        if len(all_ids) > 15:
            print(f" ... and {len(all_ids) - 15} more")
        else:
            print()
    print("="*60)


def verify_collected_images(output_path):
    """
    Verify the collected images in the output directory
    
    Args:
        output_path: Path to the IDs directory
    """
    if not os.path.exists(output_path):
        print(f"Error: Output path not found: {output_path}")
        return
    
    print("\n" + "="*60)
    print("Verification Report")
    print("="*60)
    
    id_folders = [item for item in os.listdir(output_path) 
                 if os.path.isdir(os.path.join(output_path, item))]
    
    if not id_folders:
        print("No ID folders found.")
        return
    
    print(f"Total ID folders: {len(id_folders)}")
    print()
    
    # Count images per ID
    print("Images per ID:")
    print("-"*60)
    print(f"{'ID':<20s} {'Train Images':<15s} {'Test Images':<15s} {'Total':<8s}")
    print("-"*60)
    
    total_images = 0
    total_train = 0
    total_test = 0
    
    for raptor_id in sorted(id_folders):
        id_path = os.path.join(output_path, raptor_id)
        
        try:
            all_files = os.listdir(id_path)
            image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff')
            images = [f for f in all_files if f.lower().endswith(image_extensions)]
            
            # Count train and Test images based on filename prefix
            train_images = [f for f in images if f.startswith('train_')]
            test_images = [f for f in images if f.startswith('Test_')]
            
            train_count = len(train_images)
            test_count = len(test_images)
            total_count = len(images)
            
            print(f"{raptor_id:<20s} {train_count:<15d} {test_count:<15d} {total_count:<8d}")
            
            total_images += total_count
            total_train += train_count
            total_test += test_count
            
            # Show sample filenames (to verify prefix naming)
            if images and raptor_id == sorted(id_folders)[0]:
                print(f"  Sample files:")
                for img in images[:3]:
                    print(f"    - {img}")
        except Exception as e:
            print(f"{raptor_id:<20s} Error: {e}")
    
    print("-"*60)
    print(f"{'Total:':<20s} {total_train:<15d} {total_test:<15d} {total_images:<8d}")
    print("="*60)


if __name__ == "__main__":
    # ==========================================
    # WildRaptorID Image Collection
    # ==========================================
    source_base_path = r"F:\archive\data\WildRaptorID\data\random_test_35_multi_task\Total_ID_35\Random_Samples_1\Img_Num_100"
    output_path = r"F:\archive\data\WildRaptorID\IDs"
    
    print("="*60)
    print("WildRaptorID Dataset Organization")
    print("="*60)
    print(f"Source base: {source_base_path}")
    print(f"Output: {output_path}")
    print()
    
    # Step 0: Analyze structure (recommended)
    print("STEP 0: ANALYZE STRUCTURE")
    print("="*60)
    analyze_raptor_structure(source_base_path)
    print()
    
    # Step 1: Preview collection (dry run)
    print("\n\nSTEP 1: PREVIEW MODE")
    print("="*60)
    collect_raptor_images_by_id(source_base_path, output_path, dry_run=True)
    
    # Step 2: Uncomment below to perform actual collection
    # print("\n\nSTEP 2: ACTUAL COLLECTION")
    # print("="*60)
    collect_raptor_images_by_id(source_base_path, output_path, dry_run=False)
    
    # Step 3: Verify collected images
    # print("\n\nSTEP 3: VERIFICATION")
    # verify_collected_images(output_path)