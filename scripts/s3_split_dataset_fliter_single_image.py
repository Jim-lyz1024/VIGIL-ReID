import os
import shutil
import random
from pathlib import Path
from collections import defaultdict

def split_dataset_by_image_count(ids_dir, train_dir, query_dir, gallery_dir, 
                                 train_ratio=0.6, query_ratio=0.15, gallery_ratio=0.25,
                                 seed=42):
    """
    Split turtle dataset into train/query/gallery by image count
    
    Args:
        ids_dir: Directory containing ID subfolders
        train_dir: Target directory for training images
        query_dir: Target directory for query images
        gallery_dir: Target directory for gallery images
        train_ratio: Ratio of total images for training (default: 0.6)
        query_ratio: Ratio of total images for query (default: 0.15)
        gallery_ratio: Ratio of total images for gallery (default: 0.25)
        seed: Random seed for reproducibility
    
    Strategy:
        - IDs with only 1 image -> automatically go to train
        - Calculate target image counts based on ratios
        - Select remaining IDs for train until reaching ~60% of total images
        - Use remaining IDs for query/gallery (same IDs, split images)
        - All images are used, no waste
    """
    random.seed(seed)
    
    ids_path = Path(ids_dir)
    train_path = Path(train_dir)
    query_path = Path(query_dir)
    gallery_path = Path(gallery_dir)
    
    # Create target directories
    train_path.mkdir(parents=True, exist_ok=True)
    query_path.mkdir(parents=True, exist_ok=True)
    gallery_path.mkdir(parents=True, exist_ok=True)
    
    # Get all ID folders and their image counts
    id_folders = sorted([f for f in ids_path.iterdir() 
                        if f.is_dir() and f.name.isdigit()], 
                       key=lambda x: int(x.name))
    
    if not id_folders:
        print("Error: No ID folders found!")
        return
    
    # Count images for each ID and separate single-image IDs
    id_info = []
    single_image_ids = []
    multi_image_ids = []
    total_images = 0
    
    for folder in id_folders:
        turtle_id = int(folder.name)
        image_files = sorted([f for f in folder.iterdir() 
                            if f.suffix.upper() in ['.JPG', '.JPEG', '.PNG']])
        image_count = len(image_files)
        total_images += image_count
        
        info = {
            'id': turtle_id,
            'folder': folder,
            'images': image_files,
            'count': image_count
        }
        
        if image_count == 1:
            single_image_ids.append(info)
        else:
            multi_image_ids.append(info)
    
    print("=" * 80)
    print("ReID Dataset Splitting Script (By Image Count)")
    print("=" * 80)
    print(f"Total IDs found: {len(id_folders)}")
    print(f"  - Single-image IDs: {len(single_image_ids)} (will go to train)")
    print(f"  - Multi-image IDs: {len(multi_image_ids)}")
    print(f"Total images: {total_images}")
    print(f"\nTarget distribution:")
    print(f"  Train: {train_ratio:.1%} = {int(total_images * train_ratio)} images")
    print(f"  Query: {query_ratio:.1%} = {int(total_images * query_ratio)} images")
    print(f"  Gallery: {gallery_ratio:.1%} = {int(total_images * gallery_ratio)} images")
    print(f"Random seed: {seed}")
    print("=" * 80)
    
    # Calculate target counts
    target_train = int(total_images * train_ratio)
    target_query = int(total_images * query_ratio)
    target_gallery = int(total_images * gallery_ratio)
    
    # Start with single-image IDs in training
    train_ids = single_image_ids.copy()
    train_image_count = sum(info['count'] for info in single_image_ids)
    
    print(f"\nSingle-image IDs automatically assigned to train:")
    print(f"  Count: {len(single_image_ids)} IDs, {train_image_count} images")
    
    # Shuffle multi-image IDs for random selection
    random.shuffle(multi_image_ids)
    
    # Select additional IDs for training until we reach ~60% of images
    remaining_ids = []
    
    for info in multi_image_ids:
        if train_image_count < target_train:
            train_ids.append(info)
            train_image_count += info['count']
        else:
            remaining_ids.append(info)
    
    # If we went over, adjust by moving last ID to remaining if beneficial
    if train_image_count > target_train and len(train_ids) > len(single_image_ids) + 1:
        last_id = train_ids[-1]
        # Only consider moving if it's not a single-image ID
        if last_id['count'] > 1:
            overshoot = train_image_count - target_train
            # If overshoot is significant, move last ID to remaining
            if overshoot > last_id['count'] * 0.5:
                train_ids.pop()
                remaining_ids.insert(0, last_id)
                train_image_count -= last_id['count']
    
    # Calculate images available for query/gallery
    test_image_count = total_images - train_image_count
    
    print(f"\nActual ID split:")
    print(f"  Train IDs: {len(train_ids)} (total images: {train_image_count})")
    print(f"    - Single-image: {len(single_image_ids)} IDs")
    print(f"    - Multi-image: {len(train_ids) - len(single_image_ids)} IDs")
    print(f"  Query/Gallery IDs: {len(remaining_ids)} (total images: {test_image_count})")
    print("-" * 80)
    
    # Validate: remaining_ids should all have multiple images
    single_in_test = [info for info in remaining_ids if info['count'] == 1]
    if single_in_test:
        print(f"\nWARNING: Found {len(single_in_test)} single-image IDs in query/gallery!")
        print(f"  IDs: {[info['id'] for info in single_in_test]}")
    
    # Statistics
    stats = {
        'train': {'ids': set(), 'images': 0, 'single_image_ids': 0},
        'query': {'ids': set(), 'images': 0},
        'gallery': {'ids': set(), 'images': 0}
    }
    
    # Process training IDs - use ALL images
    print("\n[1/3] Processing Training IDs...")
    for info in train_ids:
        turtle_id = info['id']
        stats['train']['ids'].add(turtle_id)
        if info['count'] == 1:
            stats['train']['single_image_ids'] += 1
        
        # Copy all images to train directory
        for img_file in info['images']:
            dst = train_path / img_file.name
            shutil.copy2(img_file, dst)
            stats['train']['images'] += 1
        
        single_marker = " (single)" if info['count'] == 1 else ""
        print(f"  ID {turtle_id}: {info['count']} images -> train{single_marker}")
    
    # Process query/gallery IDs - split images between query and gallery
    print(f"\n[2/3] Processing Query/Gallery IDs...")
    
    # Calculate query/gallery split ratio from remaining images
    test_total_ratio = query_ratio + gallery_ratio
    query_test_ratio = query_ratio / test_total_ratio
    gallery_test_ratio = gallery_ratio / test_total_ratio
    
    print(f"  Query/Gallery image split: {query_test_ratio:.1%} / {gallery_test_ratio:.1%}")
    print()
    
    for info in remaining_ids:
        turtle_id = info['id']
        stats['query']['ids'].add(turtle_id)
        stats['gallery']['ids'].add(turtle_id)
        
        # Shuffle images for this ID
        images = info['images'].copy()
        random.shuffle(images)
        
        total = len(images)
        # Split images between query and gallery
        # Ensure at least 1 image in each set
        num_query = max(1, int(total * query_test_ratio))
        # Ensure gallery also gets at least 1 image if total >= 2
        if total >= 2 and num_query >= total:
            num_query = total - 1
        
        query_images = images[:num_query]
        gallery_images = images[num_query:]
        
        # Copy query images
        for img_file in query_images:
            dst = query_path / img_file.name
            shutil.copy2(img_file, dst)
            stats['query']['images'] += 1
        
        # Copy gallery images
        for img_file in gallery_images:
            dst = gallery_path / img_file.name
            shutil.copy2(img_file, dst)
            stats['gallery']['images'] += 1
        
        print(f"  ID {turtle_id}: {len(query_images)} -> query, "
              f"{len(gallery_images)} -> gallery (total: {total})")
    
    # Print final statistics
    print("\n" + "=" * 80)
    print("Dataset Split Summary")
    print("=" * 80)
    
    print(f"\nTrain Set:")
    print(f"  IDs: {len(stats['train']['ids'])}")
    print(f"    - Single-image IDs: {stats['train']['single_image_ids']}")
    print(f"    - Multi-image IDs: {len(stats['train']['ids']) - stats['train']['single_image_ids']}")
    print(f"  Images: {stats['train']['images']} ({stats['train']['images']/total_images:.1%})")
    print(f"  ID list: {sorted(stats['train']['ids'])}")
    
    print(f"\nQuery Set:")
    print(f"  IDs: {len(stats['query']['ids'])}")
    print(f"  Images: {stats['query']['images']} ({stats['query']['images']/total_images:.1%})")
    print(f"  ID list: {sorted(stats['query']['ids'])}")
    
    print(f"\nGallery Set:")
    print(f"  IDs: {len(stats['gallery']['ids'])}")
    print(f"  Images: {stats['gallery']['images']} ({stats['gallery']['images']/total_images:.1%})")
    print(f"  ID list: {sorted(stats['gallery']['ids'])}")
    
    print(f"\nTotal:")
    print(f"  Total IDs: {len(id_folders)}")
    print(f"  Total Images: {stats['train']['images'] + stats['query']['images'] + stats['gallery']['images']}")
    print(f"  Original Total: {total_images}")
    
    # Verify
    train_ids_set = stats['train']['ids']
    test_ids_set = stats['query']['ids']
    overlap = train_ids_set.intersection(test_ids_set)
    
    all_distributed = stats['train']['images'] + stats['query']['images'] + stats['gallery']['images']
    
    print(f"\nValidation:")
    if overlap:
        print(f"   WARNING: ID overlap detected: {overlap}")
    else:
        print(f"   No ID overlap between train and query/gallery")
    
    print(f"   Query and gallery share same IDs: {stats['query']['ids'] == stats['gallery']['ids']}")
    
    if all_distributed == total_images:
        print(f"   All images distributed: {all_distributed} = {total_images}")
    else:
        print(f"   Image count mismatch: {all_distributed} != {total_images}")
    
    # Check ratios
    actual_train_ratio = stats['train']['images'] / total_images
    actual_query_ratio = stats['query']['images'] / total_images
    actual_gallery_ratio = stats['gallery']['images'] / total_images
    
    print(f"\nActual ratios:")
    print(f"  Train: {actual_train_ratio:.1%} (target: {train_ratio:.1%})")
    print(f"  Query: {actual_query_ratio:.1%} (target: {query_ratio:.1%})")
    print(f"  Gallery: {actual_gallery_ratio:.1%} (target: {gallery_ratio:.1%})")
    
    print("=" * 80)


def verify_split(train_dir, query_dir, gallery_dir):
    """
    Verify the dataset split results
    """
    train_path = Path(train_dir)
    query_path = Path(query_dir)
    gallery_path = Path(gallery_dir)
    
    print("\n" + "=" * 80)
    print("Verification Report")
    print("=" * 80)
    
    # Extract IDs from filenames
    def get_ids_from_dir(directory):
        ids = set()
        images = list(directory.glob('*.JPG')) + list(directory.glob('*.jpg')) + \
                 list(directory.glob('*.JPEG')) + list(directory.glob('*.jpeg')) + \
                 list(directory.glob('*.PNG')) + list(directory.glob('*.png'))
        
        for img in images:
            # Extract ID from filename (format: id_-1_index_original.JPG)
            parts = img.name.split('_')
            if parts:
                try:
                    turtle_id = int(parts[0])
                    ids.add(turtle_id)
                except ValueError:
                    pass
        return ids, len(images)
    
    train_ids, train_count = get_ids_from_dir(train_path)
    query_ids, query_count = get_ids_from_dir(query_path)
    gallery_ids, gallery_count = get_ids_from_dir(gallery_path)
    
    total_images = train_count + query_count + gallery_count
    
    print(f"\nDirectory Contents:")
    print(f"  Train: {train_count} images ({train_count/total_images:.1%}), {len(train_ids)} IDs")
    print(f"  Query: {query_count} images ({query_count/total_images:.1%}), {len(query_ids)} IDs")
    print(f"  Gallery: {gallery_count} images ({gallery_count/total_images:.1%}), {len(gallery_ids)} IDs")
    print(f"  Total: {total_images} images")
    
    overlap_train_query = train_ids.intersection(query_ids)
    overlap_train_gallery = train_ids.intersection(gallery_ids)
    
    print(f"\nValidation Checks:")
    if overlap_train_query:
        print(f"   Train/Query overlap: {overlap_train_query}")
    else:
        print(f"   No Train/Query overlap")
    
    if overlap_train_gallery:
        print(f"   Train/Gallery overlap: {overlap_train_gallery}")
    else:
        print(f"   No Train/Gallery overlap")
    
    if query_ids == gallery_ids:
        print(f"   Query and Gallery share same IDs")
    else:
        print(f"   Query and Gallery have different IDs")
    
    print("=" * 80)


if __name__ == "__main__":
    # Configuration
    ############# Change here to specify new dataset #############
    base_dir = r"F:\archive\data\HumpbackWhaleID"
    ##########################
    ids_directory = os.path.join(base_dir, "IDs")
    train_directory = os.path.join(base_dir, "train")
    query_directory = os.path.join(base_dir, "query")
    gallery_directory = os.path.join(base_dir, "gallery")
    
    print("Turtle Dataset Split for ReID Task (By Image Count)")
    print("=" * 80)
    print(f"Source: {ids_directory}")
    print(f"Train: {train_directory}")
    print(f"Query: {query_directory}")
    print(f"Gallery: {gallery_directory}")
    print("=" * 80)
    print("\nSplit Strategy:")
    print("  - Allocate IDs to train until ~60% of total images")
    print("  - Remaining IDs -> query + gallery (same IDs)")
    print("  - For query/gallery: split their images ~15%/25%")
    print("  - ALL images will be used")
    print("=" * 80)
    
    split_dataset_by_image_count(
            ids_dir=ids_directory,
            train_dir=train_directory,
            query_dir=query_directory,
            gallery_dir=gallery_directory,
            train_ratio=0.6,
            query_ratio=0.15,
            gallery_ratio=0.25,
            seed=42
        )
        
        # Verify the split
    # verify_split(train_directory, query_directory, gallery_directory)
